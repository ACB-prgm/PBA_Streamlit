from streamlit_option_menu import option_menu
import streamlit_pages
import streamlit as st
import pandas as pd
import subprocess
import theme
import time
import os


# ALL PAGES —————————————————————————————————————————————————————————————————————————————————
st.set_page_config('626 Buget Analysis', page_icon=":chart_with_upwards_trend:", layout="wide")
st.markdown(theme.FONT_CHANGE_CSS, unsafe_allow_html=True)

CSSS = pd.read_excel("626_budget_analysis.xlsx", sheet_name="CSSS")
CSSS.DATE = pd.to_datetime(CSSS.DATE).dt.date

PO = pd.read_excel("626_budget_analysis.xlsx", sheet_name="PO")
PO.DATE = pd.to_datetime(PO.DATE).dt.date


reset = st.button("RESET FILTERS")
if reset or not st.session_state.get("session"):
    st.session_state.clear()
    session = str(time.time())
    st.session_state["session"] = session
else:
    session = st.session_state.session

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
    "PURCHASE ORDER LOGS"
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

if __name__ == "__main__":
    if not st.secrets.get("PRODUCTION") and not os.environ.get("streamlit_started"):
        os.environ["streamlit_started"] = "True"
        subprocess.run(["streamlit", "run", os.path.abspath(__file__)])
