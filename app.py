from streamlit_option_menu import option_menu
import streamlit_pages
import streamlit as st
import pandas as pd
import AuthManager
import subprocess
import theme
import time
import os


st.set_page_config('626 Buget Analysis', page_icon=":chart_with_upwards_trend:", layout="wide")
st.markdown(theme.FONT_CHANGE_CSS, unsafe_allow_html=True)

ADMIN_NAME = ""
ADMIN_PASS = ""
PASSWORD = ""

def main():
    # ALL PAGES —————————————————————————————————————————————————————————————————————————————————
    if not st.session_state.get("data_cache_key"):
        st.session_state["data_cache_key"] = str(time.time())

    reset = st.button("RESET FILTERS")
    if reset or not st.session_state.get("session"):
        data_cache_key = st.session_state.get("data_cache_key")
        logged_in = st.session_state.get("logged_in")

        st.session_state.clear()
        session = str(time.time())
        st.session_state["session"] = session

        st.session_state["data_cache_key"] = data_cache_key
        st.session_state["logged_in"] = logged_in
    else:
        session = st.session_state.session

    @st.cache_data
    def load_data(cache_key):
        CSSS = pd.read_excel("626_budget_analysis.xlsx", sheet_name="CSSS")
        CSSS.DATE = pd.to_datetime(CSSS.DATE).dt.date
        # TEMP MITIGATION FOR VARIANCE ISSUE
        CSSS["VARIANCE (%)"] = ((CSSS["ACTUAL"] - CSSS["ESTIMATE"]) / CSSS["ESTIMATE"]) * 100
        CSSS["VARIANCE (%)"] = CSSS["VARIANCE (%)"].apply(lambda x: -100 if x < -100 else (100 if x > 100 else x))

        PO = pd.read_excel("626_budget_analysis.xlsx", sheet_name="PO") 
        PO.DATE = pd.to_datetime(PO.DATE).dt.date

        PR = pd.read_excel("626_budget_analysis.xlsx", sheet_name="PR") 
        PR["VARIANCE (%)"] = ((PR["ACTUAL"] - PR["EST"]) / PR["EST"]) * 100
        PR["VARIANCE (%)"] = PR["VARIANCE (%)"].apply(lambda x: -100 if x < -100 else (100 if x > 100 else x))

        return CSSS, PO, PR

    CSSS, PO, PR = load_data(st.session_state.get("data_cache_key"))


    with st.container():
        cols = st.columns(4)
        with cols[0]:
            sel_sections = st.multiselect("SECTIONS", CSSS["SECTION"].unique(), key="s_" + session)
        with cols[1]:
            sel_projects = st.multiselect("PROJECTS", CSSS["PROJECT NAME"].unique(), key="p_" + session)
        with cols[2]:
            start_date = st.date_input('START DATE', CSSS.DATE.min(), key="sd_" + session)
        with cols[3]:
            end_date = st.date_input('END DATE', CSSS.DATE.max(), key="ed_" + session)

    for df in [CSSS, PO]:
        if sel_sections:
            drop_indices = df[~df["SECTION"].isin(sel_sections)].index
            df.drop(drop_indices, inplace=True)
        if sel_projects:
            drop_indices = df[~df["PROJECT NAME"].isin(sel_projects)].index
            df.drop(drop_indices, inplace=True)
        if start_date < end_date:
            drop_indices = df[~((df['DATE'] > start_date) & (df['DATE'] < end_date))].index
            df.drop(drop_indices, inplace=True)
        elif start_date == end_date:
            pass
        else:
            st.error('Error: End date must fall after start date.')



    # PAGE SPECIFFIC —————————————————————————————————————————————————————————————————————————————————
    pages = [
        "HOME",
        "COST SUMMARY",
        "COST SUMMARY TABLE VIEW",
        "COST SUMMARY OVER TIME",
        "PURCHASE ORDER LOGS",
        "PAYROLL"
    ]

    with st.sidebar:
        selected_page = option_menu(
            None, pages,
            styles={"container" : {"background-color" : "rgba(0,0,0,0)"}}
        )

    if selected_page == "HOME":
        streamlit_pages.home()
    else:
        st.title(selected_page)
        if selected_page == pages[1]:
            streamlit_pages.cost_summary(CSSS)
        elif selected_page == pages[2]:
            streamlit_pages.cost_summary_table_view(CSSS)
        elif selected_page == pages[3]:
            streamlit_pages.cost_summary_time(CSSS)
        elif selected_page == pages[4]:
            streamlit_pages.purchase_order_logs(PO)
        elif selected_page == pages[5]:
            streamlit_pages.payroll(PR)

def log_in():
    st.title("LOGIN")
    option = st.radio("SELECT LOGIN TYPE", ["ADMIN LOG IN", "VIEWER LOG IN", "CREATE ADMIN ACCOUNT"])
    
    if option == "ADMIN LOG IN":
        with st.form("admin_login"):
            attempt = (st.text_input("ENTER USERNAME", placeholder="USERNAME"), st.text_input("ENTER PASSWORD", type="password", placeholder="PASSWORD"))
            form_complete = attempt[0] != "" and attempt[1] != ""
            if st.form_submit_button("LOG IN AS ADMIN") and form_complete or form_complete:
                ERR = AuthManager.admin_login(attempt[0], attempt[1])
                if ERR:
                    st.write(ERR)
                else:
                    st.session_state["logged_in"] = True
                    st.experimental_rerun()

    elif option == "VIEWER LOG IN":
        with st.form("viewer_login"):
            attempt = (st.text_input("ENTER USERNAME", placeholder="USERNAME"), st.text_input("ENTER PASSWORD", type="password", placeholder="PASSWORD"))
            form_complete = attempt[0] != "" and attempt[1] != ""
            if st.form_submit_button("LOG IN AS VIEWER") and form_complete or form_complete:
                ERR = AuthManager.viewer_login(attempt[0], attempt[1])
                if ERR:
                    st.write(ERR)
                else:
                    st.session_state["logged_in"] = True
                    st.experimental_rerun()
    
    elif option == "CREATE ADMIN ACCOUNT":
        if not st.session_state.get("create_form_complete"):
            with st.form("create_account"):
                info = (
                    st.text_input("ENTER A USERNAME", placeholder="USERNAME"),
                    st.text_input("ENTER A PASSWORD", type="password", placeholder="PASSWORD"),
                    st.text_input("CONFIRM PASSWORD", type="password", placeholder="PASSWORD"),
                    st.text_input("ENTER A VIEWER USERNAME", placeholder="VIEWER USERNAME", help="This will be the USERNAME you share with people you want to be able to view the site."),
                    st.text_input("ENTER A VIEWER PASSWORD", placeholder="VIEWER PASSWORD", help="This will be the PASSWORD you share with people you want to be able to view the site."), 
                )
                form_complete = not True in [x == "" for x in info]
                if st.form_submit_button("SUBMIT") and form_complete or form_complete:
                    if info[1] != info[2]:
                        st.write("YOUR PASSWORDS DO NOT MATCH")
                    else:
                        account_info = {
                                "username" : info[0],
                                "password" : info[1],
                                "viewer" : info[3],
                                "viewer_password" : info[4]
                            }
                        ERR = AuthManager.create_admin(account_info)
                        if ERR:
                            st.write(ERR)
                        else:
                            st.session_state["create_form_complete"] = 1
                            st.session_state["account_info"] = account_info
                            st.experimental_rerun()
        elif st.session_state["create_form_complete"] == 1:
            account_info = st.session_state["account_info"]
            if not st.session_state.get("dbx_auth_token_info"):
                AuthManager.authorize(account_info)
            elif not st.session_state.get("google_auth_token_info"):
                AuthManager.authorize(account_info, "google")
            else:
                st.session_state["logged_in"] = True
                st.experimental_rerun()
                    

if st.session_state.get("logged_in"):
    main()
else:
    log_in()


if __name__ == "__main__":
    if not st.secrets.get("PRODUCTION") and not os.environ.get("streamlit_started"):
        os.environ["streamlit_started"] = "True"
        subprocess.run(["streamlit", "run", os.path.abspath(__file__)])
