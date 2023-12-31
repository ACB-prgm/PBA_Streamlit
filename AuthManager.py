from streamlit.components.v1 import html
import streamlit as st
import requests
import gspread
import hashlib
import base64
import boto3
import json
import uuid
import time
import os


AUTH_API_URL = "https://opalescent-agate-lemon.glitch.me"
AUTH_API_STORE_ENDPOINT = os.path.join(AUTH_API_URL, "auth/store")
AUTH_API_LOGIN_ENDPOINT = os.path.join(AUTH_API_URL, "auth/login/")
AUTH_API_CHECK_ENDPOINT = os.path.join(AUTH_API_URL, "auth/check/")
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

requests.get(AUTH_API_URL) # Ping the server to make sure it is awake


@st.cache_data
def dbx_token_valid(token) -> bool:
    headers = {
        'Authorization': f'Bearer {token}',
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

@st.cache_data
def refresh_dbx_token(refresh_token) -> bool:
    secrets = get_dbx_secrets()
    data = {
        'grant_type' : 'refresh_token',
        'refresh_token' : refresh_token,
    }
    # Prepare the headers
    auth = base64.b64encode(f"{secrets['client_id']}:{secrets['client_secret']}".encode()).decode()
    headers = {'Authorization': f"Basic {auth}",}

    # # Make the POST request
    response = requests.post(secrets["token_uri"], headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        st.session_state["dbx_auth_token_info"] = response.json()
        return True
    else:
        print(f"Request failed with status {response.status_code}")
        return False

@st.cache_data
def google_token_valid(token) -> bool:
    response = requests.get(GOOGLE_CHECK_TOKEN_URL, params={'access_token': token})

    if response.status_code == 200:
        return True
    else:
        return False

@st.cache_data
def get_google_secrets() -> dict:
    secrets = json.loads(s3.get_object(Bucket=BUCKET, Key=GOOGLE_OAUTH_SECRETS)["Body"].read())["web"]
    return secrets

@st.cache_data
def get_dbx_secrets() -> dict:
    secrets = json.loads(s3.get_object(Bucket=BUCKET, Key=DBX_OAUTH_SECRETS)["Body"].read())
    return secrets

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

def create_gspread_client(account_info):
    if not account_info.get("google_refresh_token"):
        print("ACCOUNT DOES NOT HAVE A REFRESH TOKEN")
        raise(NotImplementedError)

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

@st.cache_data
def get_auth_api_params(account_info, service="dbx") -> dict:
    if service == "dbx":
        secrets = get_dbx_secrets()
    else:
        secrets = get_google_secrets()
    
    params = {
        "auth_uri" : secrets["auth_uri"],
        "token_uri" : secrets["token_uri"],
        "auth_params" : {
            "client_id" : secrets["client_id"],
            'response_type': 'code',
            # 'force_reapprove': 'true',
            'token_access_type' : 'offline',
            'state' : account_info["ID"]
        },
        "token_params" : {
            "client_id" : secrets["client_id"],
            "client_secret" : secrets["client_secret"]
        }
    }

    if service == "google":
        params["auth_params"]["scope"] = GOOGLE_SCOPES
    
    return params

@st.cache_data
def hash(input_string:str) -> str:
    return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

def nav_to(url, message="Click here if you are not redirected automatically!"):
    js = f'<script>window.open("{url}", "_blank");</script>'
    html(js)
    st.write(f'''<a target="_blank" href="{url}">
                                <button>
                                    {message}
                                </button>
                            </a>''',
                       unsafe_allow_html=True
                        )


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
        info["password"] = hash(info.get("password"))
        info["viewer_password"] = hash(info.get("viewer_password"))
        info["ID"] = str(uuid.uuid4())
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
    st.session_state.account_info = info
    s3.put_object(Bucket=BUCKET, Key=ADMINS_INFO, Body=json.dumps(admins))

def get_admin_info(admin:str) -> dict:
    try:
        admins = json.loads(s3.get_object(Bucket=BUCKET, Key=ADMINS_INFO)["Body"].read())
    except:
        return None
    return admins.get(admin)

def login(account_info, service="dbx"):
    token_info = account_info.get(f"{service}_auth_token_info") or st.session_state.get(f"{service}_auth_token_info") or {}
    token_valid = globals()[f"{service}_token_valid"](token_info.get("access_token"))

    if token_valid:
        return
    elif token_info.get("refresh_token") and not token_valid:
        success = globals()[f"refresh_{service}_token"](token_info.get("refresh_token"))
        if not success:
            authorize(account_info, service)
    else:
        authorize(account_info, service)

def admin_login(admin:str, password:str):
    admin_info = get_admin_info(admin)
    
    if not admin_info:
        return "ADMIN NOT FOUND"
    if hash(password) != admin_info.get("password"):
        return "INCORRECT PASSWORD"
    
    for service in ["dbx", "google"]:
        if st.session_state.get(f"{service}_auth_token_info"):
            admin_info[f"{service}_auth_token_info"] = st.session_state[f"{service}_auth_token_info"]
        else:
            login(admin_info, service)
    
    update_admin(admin_info)
    st.session_state["account_info"] = admin_info

@st.cache_data
def get_viewer_info(viewer:str) -> dict:
    try:
        viewers = json.loads(s3.get_object(Bucket=BUCKET, Key=VIEWERS_INFO)["Body"].read())
    except:
        return None
    return viewers.get(viewer)

@st.cache_data
def viewer_login(viewer:str, password:str):
    viewer_info = get_viewer_info(viewer)

    if not viewer_info:
        return "VIEWER NOT FOUND"
    if hash(password) != viewer_info.get("password"):
        return "INCORRECT PASSWORD"
    
    st.session_state.account_info = get_admin_info(viewer_info.get("admin"))     

def authorize(account_info, service="dbx"):
    if not st.session_state.get("auth_state"):
        st.session_state["auth_state"] = 0
    
    if st.session_state["auth_state"] == 0:
        response = requests.put(
            AUTH_API_STORE_ENDPOINT,
            json=get_auth_api_params(account_info, service)
        )
        serve_name = "Dropbox" if service == "dbx" else service.title()
        nav_to(AUTH_API_LOGIN_ENDPOINT + account_info["ID"], f"Click here to sign in to {serve_name} if you are not redirected automatically")
        st.session_state["auth_state"] = 1
        time.sleep(4)
        st.experimental_rerun()
    elif st.session_state["auth_state"] == 1:
        response =requests.get(AUTH_API_CHECK_ENDPOINT + account_info["ID"])
        if response.status_code == 200:
            st.session_state["auth_state"] = 0
            st.session_state[f"{service}_auth_token_info"] = response.json()
            st.experimental_rerun()
        elif response.status_code == 201:
            time.sleep(1)
            st.experimental_rerun()
        else:
            print(response.text)    

# def st_oauth(account_info, service="dbx") -> None:
#     scopes = "" if service == "dbx" else GOOGLE_SCOPES
#     if account_info.get(f"{service}_token"):
#         oauth2.refresh_token(account_info.get(f"{service}_token"))
#         return None

#     if service == "dbx":
#         msg = "AUTHORIZE DROPBOX"
#     else:
#         msg = "AUTHORIZE GOOGLE DRIVE"
#     result = oauth2.authorize_button(msg, APP_URL, scopes)

#     if result and result.get("token"):
#         token = result.get('token')
#         account_info[f"{service}_token"] = token
#         st.session_state[f"{service}_authorized"] = True
#         update_admin(account_info)
#         st.experimental_rerun()
