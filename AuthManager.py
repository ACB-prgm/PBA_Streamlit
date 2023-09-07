from streamlit_oauth import OAuth2Component
from urllib.parse import urlencode
import streamlit as st
import requests
import gspread
import base64
import boto3
import json
import time
import os


DBX_CHECK_TOKEN_URL = "https://api.dropboxapi.com/2/check/user"
GOOGLE_CHECK_TOKEN_URL = "https://www.googleapis.com/oauth2/v1/tokeninfo"

# S3 PATHS
BUCKET = "626-api-info"
GOOGLE_OAUTH_SECRETS = "google_oauth_client_secrets.json"
GOOGLE_TOKENS = "google_tokens.json"
DBX_OAUTH_SECRETS = "dbx_secrets.json"
DBX_TOKENS = "dbx_tokens.json"
DBX_LINK = "dbx_link.txt"
ADMINS_INFO = "admin_info.json"
VIEWERS_INFO = "viewers_info.json"

GOOGLE_SCOPES = "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive"

if st.secrets.get("PRODUCTION"):
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["AWS_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS_SECRET"]
    APP_URL = "https://pba-st.streamlit.app/"
else:
    APP_URL = "http://localhost:8501"

s3 = boto3.client("s3")


def dbx_auth_url() -> str:
    # Redirect the user to the Dropbox authorization URL
    secrets = get_dbx_secrets()
    params = {
        'response_type': 'code',
        'client_id': secrets["client_id"],
        'redirect_uri': secrets["redirect_uri"],
        'force_reapprove': 'true',
        'token_access_type' : 'offline'
    }
    return f"{secrets['auth_uri']}?{urlencode(params)}"

def google_auth_url() -> str:
    gsecrets = get_google_secrets()
    params = {
        "client_id" : gsecrets["client_id"],
        "redirect_uri" : gsecrets["redirect_uri"],
        "response_type" : "code",
        "scope" : " ".join(GOOGLE_SCOPES),
        "access_type" : "offline"
    }
    return f"{gsecrets['auth_uri']}?{urlencode(params)}"

def dbx_token_valid() -> bool:
    headers = {
        'Authorization': f'Bearer {os.environ.get("dbx_access_token")}',
        "Content-Type": "application/json",
    }
    data = {'query':'user'}
    response = requests.post(DBX_CHECK_TOKEN_URL, headers=headers, data=data)

    if response.status_code != 401: # 401 is unauthorized
        # Token is valid
        return True
    else:
        # Token is invalid or expired
        return False

def refresh_dbx_token() -> bool:
    if not os.environ.get("dbx_refresh_token"):
        return False
    secrets = get_dbx_secrets()
    data = {
        'grant_type' : 'refresh_token',
        'refresh_token' : os.environ["dbx_refresh_token"],
    }
    # Prepare the headers
    auth = base64.b64encode(f"{secrets['client_id']}:{secrets['client_secret']}".encode()).decode()
    headers = {'Authorization': f"Basic {auth}",}

    # # Make the POST request
    response = requests.post(secrets["token_uri"], headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        update_s3_tokens("dbx", response.json())
        return True
    else:
        print(f"Request failed with status {response.status_code}")
        return False

def google_token_valid() -> bool:
    token = os.environ.get("google_access_token")
    response = requests.get('{}?access_token={}'.format(GOOGLE_CHECK_TOKEN_URL, token))

    if response.status_code == 200:
        return True
    else:
        return False

def refresh_google_token() -> bool:
    secrets = get_google_secrets()

    data = {
    'client_id': secrets["client_id"],
    'client_secret': secrets["client_secret"],
    'refresh_token': os.environ["google_refresh_token"],
    'grant_type': 'refresh_token',
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data)
    if response.status_code == 200:
        update_s3_tokens("google", response.json())
        return True
    else:
        return False

def get_google_secrets() -> dict:
    secrets = json.loads(s3.get_object(Bucket=BUCKET, Key=GOOGLE_OAUTH_SECRETS)["Body"].read())["web"]
    return secrets

def get_dbx_secrets() -> dict:
    secrets = json.loads(s3.get_object(Bucket=BUCKET, Key=DBX_OAUTH_SECRETS)["Body"].read())
    return secrets

def get_s3_tokens(service):
    if service == "dbx":
        key = DBX_TOKENS
    elif service == "google":
        key = GOOGLE_TOKENS

    try:
        tokens = json.loads(s3.get_object(Bucket=BUCKET, Key=key)["Body"].read())
    except:
        tokens = {"access_token":"", "refresh_token":""}

    return tokens

def update_s3_tokens(service, response):
    s3_tokens = get_s3_tokens(service)

    for token in ["access_token", "refresh_token"]:
        if response.get(token):
            os.environ["%s_%s" % (service, token)] = response[token]
            s3_tokens[token] = response[token]
    
    if service == "dbx":
        key = DBX_TOKENS
    elif service == "google":
        key = GOOGLE_TOKENS
    
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(s3_tokens))

def populate_environ_tokens() -> None:
    for service in ["dbx", "google"]:
        tokens = get_s3_tokens(service)
        for token in ["access_token", "refresh_token"]:
            os.environ["%s_%s" % (service, token)] = tokens[token]

def upload_dfs_to_google_sheet(dfs:dict, sheet_name:str):
    gc = create_gspread_client()

    try:
        # Try to open the Google Sheet if it exists
        sheet = gc.open(sheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        # Create a new Google Sheet if it doesn't exist
        sheet = gc.create(sheet_name)


    for idx, df_name in enumerate(dfs):
        df = dfs.get(df_name)
        try:
            worksheet = sheet.get_worksheet(idx)
            worksheet.clear()
            worksheet.update_title(df_name)
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(df_name, len(df), len(df.columns))
        
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    # sheet.share(share_email, "user", "writer", notify=False)

def create_gspread_client():
    secrets = get_google_secrets()
    auth_user = {
        "refresh_token": os.environ.get("google_refresh_token"),
        "token_uri": secrets["token_uri"],
        "client_id": secrets["client_id"],
        "client_secret": secrets["client_secret"],
    }

    gc, _ = gspread.oauth_from_dict(authorized_user_info=auth_user)

    return gc

def link_exists() -> bool:
    if os.environ.get("dbx_link"):
        return True

    try:
        link = s3.get_object(Bucket=BUCKET, Key=DBX_LINK)["Body"].read().decode('utf-8')
        os.environ["dbx_link"] = link
        return True
    except:
        return False

def update_dbx_link(link) -> None:
    os.environ["dbx_link"] = link
    s3.put_object(Bucket=BUCKET, Key=DBX_LINK, Body=link)

def get_st_auth_args(service="dbx") -> dict:
    if service == "dbx":
        secrets = get_dbx_secrets()
    else:
        secrets = get_google_secrets()
    
    return {
        "client_id" : secrets["client_id"],
        "client_secret" : secrets["client_secret"],
        "authroize_endpoint" : secrets["auth_uri"],
        "token_endpoint" : secrets["token_uri"],
        "refresh_token_endpoint" : secrets["token_uri"],
        "revoke_token_endpoint" : secrets["token_uri"]
    }

@st.cache_data
def create_admin(info):
    # PULL THE ADMINS INFO
    try:
        admins = json.loads(s3.get_object(Bucket=BUCKET, Key=ADMINS_INFO)["Body"].read())
        viewers = json.loads(s3.get_object(Bucket=BUCKET, Key=VIEWERS_INFO)["Body"].read())
    except:
        admins = {}
        viewers = {}

    # CHECK IF NAME IS TAKEN AND UPDATE LOCALLY
    if info.get("username") in admins:
        return "ADMIN USERNAME ALREADY EXISTS"
    elif info.get("viewer") in viewers:
        return "VIEWER USERNAME ALREADY EXISTS"
    else:
        admins[info.get("username")] = info
        viewers[info.get("viewer")] = {
            "password" : info.get("viewer_password"),
            "admin" : info.get("username")
        }

    # UPDATE GLOBALLY
    s3.put_object(Bucket=BUCKET, Key=ADMINS_INFO, Body=json.dumps(admins))
    s3.put_object(Bucket=BUCKET, Key=VIEWERS_INFO, Body=json.dumps(viewers))

def update_admin(info:dict) -> None:
    admins = json.loads(s3.get_object(Bucket=BUCKET, Key=ADMINS_INFO)["Body"].read())
    admins[info.get("username")] = info
    s3.put_object(Bucket=BUCKET, Key=ADMINS_INFO, Body=json.dumps(admins))

def get_admin_info(admin:str) -> dict:
    admins = json.loads(s3.get_object(Bucket=BUCKET, Key=ADMINS_INFO)["Body"].read())
    return admins.get(admin)

def st_oauth(account_info, service="dbx") -> None:
    oauth2 = OAuth2Component(**get_st_auth_args(service))
    scopes = "" if service == "dbx" else GOOGLE_SCOPES

    if service == "dbx":
        msg = "AUTHORIZE DROPBOX"
    else:
        msg = "AUTHORIZE GOOGLE DRIVE"
    result = oauth2.authorize_button(msg, APP_URL, scopes)

    if result and result.get("token"):
        print(service)
        token = result.get('token')
        account_info[f"{service}_token"] = token
        st.session_state[f"{service}_authorized"] = True
        update_admin(account_info)
        st.experimental_rerun()
