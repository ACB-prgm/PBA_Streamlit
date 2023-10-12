from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import AuthManager
import theme
import time


METRICS = ["VARIANCE", "VARIANCE (%)", "ESTIMATE", "ACTUAL"]
FINANCIAL = ["VARIANCE", "ESTIMATE", "ACTUAL", "EST"]

# HELPERS ———————————————————————————————————————————————————————————————————————————————————————————————————————
def add_v_space(size:int=1) -> None:
    st.markdown("".join(["<br/>" for _ in range(size)]), unsafe_allow_html=True)

def create_sel_bar_plot(df, height=500):
    if st.session_state.get("cs_section_colors"):
        colors = st.session_state.cs_section_colors
    else:
        colors = [theme.PRIMARY_COLOR for _ in range(len(df))]

    fig = go.Figure(data=[go.Bar(
        x=df.index, 
        y=df["VARIANCE"],
        customdata=df.index,
        name="VARIANCE",
        marker=dict(color=colors)
    )])
    fig.update_layout(
        xaxis_title="SECTION",
        yaxis_title="VARIANCE",
        font={"size" : 12}
    )
    avg = df["VARIANCE"].mean()
    fig.add_trace(go.Scatter(
        x=[df.index[0], df.index[-1]],
        y=[avg, avg],
        name='AVERAGE',
        mode='lines',
        line=dict(color=theme.SECONDARY_COLOR, width=2, dash='dash'))
    )

    sel_section = plotly_events(fig, override_height=f"{height}px", select_event=True)
    if sel_section:
        new_colors = [theme.PRIMARY_COLOR for _ in range(len(df))]
        sel_x = [sel.get("x") for sel in sel_section]

        if st.session_state.get("cs_sel_section") == sel_x:
            st.session_state.cs_sel_section = None
        else:
            st.session_state.cs_sel_section = sel_x
            for sel in sel_section:
                new_colors[sel.get("pointIndex")] = theme.SECONDARY_COLOR
        
        st.session_state.cs_section_colors = new_colors
        st.experimental_rerun()

def highlight(row, to_highlight, color="#FFFFFF"):
    if any(item in to_highlight for item in row.values):
        return [f'color:{color}; font-weight:bold'] * len(row)
    else:
        return [f'color:{theme.BG_COLOR_PRIMARY}'] * len(row)


def highlight_with_opacity(val, var_pct):
    opacity = max(round(abs(min(abs(var_pct), 100)) / 100.0, 2), .25)
    if val > 0:
        color = theme.RED_RGBA
    elif val < 0:
        color = theme.GREEN_RGBA
    else:
        return f'background-color: {theme.BG_COLOR_SECONDARY}'
    
    color = list(color)
    color[-1] = opacity
    return f'background-color: rgba{str(tuple(color))}'


def st_df(df:pd.DataFrame, keep_percent=False, highlight_text=False, editable=False, **kwargs):
    display_df = df.copy()
    if "VARIANCE (%)" in df.columns:
        variance_percent_series = df["VARIANCE (%)"]
        
        # Drops Var% if only using for the purposes of determining the higlight opacity
        if not keep_percent:
            display_df.drop("VARIANCE (%)", axis=1, inplace=True)

        # Apply red/green highlighting
        styled_df = display_df.style.apply(lambda row: [highlight_with_opacity(row["VARIANCE"], variance_percent_series[row.name]) for _ in row], axis=1)
    else:
        styled_df = display_df.style

    # Highlights if a selectable chart
    if highlight_text:
        styled_df = styled_df.apply(highlight, axis=1, to_highlight=st.session_state.cs_sel_section)
    
    # Apply financial formatting
    col_style = {}
    for metric in FINANCIAL:
        if metric in display_df.columns:
            col_style[metric] = "${:,.2f}"
    
    if keep_percent:
        col_style["VARIANCE (%)"] = "{:.2f}"
    styled_df = styled_df.format(col_style)

    if editable:
        return st.data_editor(styled_df, **kwargs)
    
    return st.dataframe(styled_df, **kwargs)


# PAGES —————————————————————————————————————————————————————————————————————————————————————————————————————————
def home():
    add_v_space(2)
    st.image(theme.logo_img)
    with st.container():
        cols = st.columns(3)
        with cols[1]:
            st.markdown("### PRODUCTION BUDGET ANALYSIS")
        add_v_space(2)

        dbx_link = st.session_state["account_info"].get("dbx_link", "")
        dbx_link_entry = st.text_input(
            "DROPBOX LINK:",
            dbx_link,
            placeholder="eg. https://www.dropbox.com/home/_JOB_ACTUALS"
            )
        if dbx_link_entry != dbx_link:
            st.session_state["account_info"]["dbx_link"] = dbx_link_entry
            AuthManager.update_admin(st.session_state["account_info"])
            st.experimental_rerun()

        if dbx_link_entry:
            refresh = st.button("REFRESH DATA")
            if refresh:
                st.session_state["data_cache_key"] = str(time.time())
                st.experimental_rerun()
            
    add_v_space(2)
    with st.empty():
        cols = st.columns(3)
        with cols[-1]:
            st.image(theme.stamp_img, width=500)

def cost_summary(CSSS):
    st.markdown("### AVERAGE VARIANCE BY SECTION")
    st.divider()

    with st.container():
        df = CSSS.groupby("SECTION").mean(numeric_only=True).sort_values(by="VARIANCE", ascending=False)
        
        cols = st.columns([0.3, 0.7])
        with cols[0]:
            highlight_text = False
            display_df = df[["VARIANCE", "VARIANCE (%)"]].reset_index(drop=False)
            if st.session_state.get("cs_sel_section"):
                check_df = CSSS[CSSS["SECTION"].isin(st.session_state.cs_sel_section)]
                if not check_df.empty:
                    highlight_text = True
            
            st_df(display_df, use_container_width=True, highlight_text=highlight_text, height=550, hide_index=True)
        with cols[1]:
            if st.session_state.get("cs_sel_section"):
                if not check_df.empty:
                    CSSS = check_df
                st.markdown("#### {} SECTION(S) AVERAGE METRICS".format(", ".join(st.session_state.cs_sel_section)))
            else:
                st.markdown("#### AGGREGATE AVERAGE METRICS")
            
            avgs = CSSS[METRICS].mean().to_frame().T
            st_df(avgs, keep_percent=True, hide_index=True, use_container_width=True)
            with st.empty():
                create_sel_bar_plot(df)

    
    st.markdown("### AVERAGE VARIANCE BY SUBSECTION")
    st.divider()
    
    with st.container():
        df = CSSS.groupby("SUB SECTION").mean(numeric_only=True).sort_values(by="VARIANCE", ascending=False)
        
        cols = st.columns([0.3, 0.7])
        with cols[0]:
            st_df(df[["VARIANCE", "VARIANCE (%)"]], keep_percent=True, use_container_width=True)
        with cols[1]:
            fig = px.bar(
                df,
                df.index,
                df["VARIANCE"],
            )
            fig.update_layout(plot_bgcolor = theme.BG_COLOR_PRIMARY)
            st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown("### AVERAGE VARIANCE BY PROJECT")
    st.divider()

    with st.container():
        df = CSSS.groupby("PROJECT NAME").mean(numeric_only=True).sort_values(by="VARIANCE", ascending=False)
        
        cols = st.columns([0.3, 0.7])
        with cols[0]:
            st_df(df[["VARIANCE", "VARIANCE (%)"]], keep_percent=True, use_container_width=True)
        with cols[1]:
            fig = px.bar(
                df,
                df.index,
                df["VARIANCE"],
            )
            fig.update_layout(plot_bgcolor = theme.BG_COLOR_PRIMARY)
            st.plotly_chart(fig, use_container_width=True, theme=None)


def cost_summary_table_view(CSSS:pd.DataFrame):
    df_to_show = CSSS.copy()[["SECTION", "SUB SECTION", "VARIANCE", "VARIANCE (%)", "ESTIMATE", "ACTUAL"]]

    if st.checkbox("BY SUBSECTION"):
        df_to_show = df_to_show.groupby(["SECTION", "SUB SECTION"]).mean(numeric_only=True).reset_index()
        # df_to_show['SECTION'] = df_to_show['SECTION'].mask(df_to_show['SECTION'].duplicated(), '')
    else:
        df_to_show = df_to_show.groupby("SECTION").mean(numeric_only=True).reset_index()

    st_df(df_to_show, keep_percent=True, use_container_width=True, hide_index=True)


def cost_summary_time(CSSS):
    df = CSSS.groupby("SECTION").mean(numeric_only=True).sort_values(by="VARIANCE", ascending=False)
    create_sel_bar_plot(df, 450)

    if st.session_state.get("cs_sel_section"):
        df = CSSS[CSSS["SECTION"].isin(st.session_state.cs_sel_section)]
    else:
        df = CSSS.copy()

    df = df.groupby(["SECTION", "DATE"]).agg({
        'VARIANCE': 'mean',
        'PROJECT NAME': lambda x: ', '.join(set(x))
    }).reset_index().sort_values(by="DATE")

    

    sorter_df = CSSS.groupby(["SECTION", "DATE"]).mean(numeric_only=True)
    fig = px.line(
        df, x="DATE", y="VARIANCE", range_y=(sorter_df.VARIANCE.min()*1.2, sorter_df.VARIANCE.max()*1.2),
        color="SECTION", hover_data="PROJECT NAME", 
        template = theme.template_name)
    fig.update_traces(mode='lines+markers')
    fig.update_layout(yaxis=dict(
            automargin=True,
            showgrid=True,
            gridcolor=theme.LINE_COLOR,
            gridwidth=1,
            zerolinecolor=theme.LINE_COLOR,
            zerolinewidth=3
        ))

    if len(df.SECTION.unique()) > 1:
        fig.update_traces(opacity=0.7)
        avg = df.groupby("DATE").mean(numeric_only=True).reset_index()
        avg["SECTION"] = "SECTIONS AVERAGE"
        avg["PROJECT NAME"] = "ALL IN SELECTED RANGE"

        fig.add_trace(
            go.Scatter(
                x=avg.DATE, y=avg.VARIANCE, hovertext=avg["PROJECT NAME"],
                mode='lines+markers', line=dict(color=theme.SECONDARY_COLOR, width=5, dash='dash'),
                name= "AVERAGE"
            ))

    st.plotly_chart(fig, use_container_width=True)


def purchase_order_logs(PO):
    df = PO[["PAYEE", "ACTUAL", "PROJECT NAME"]]
    counts = df.groupby("PAYEE").size().reset_index(name='COUNT')
    df = pd.merge(df, counts, on="PAYEE").sort_values(by="ACTUAL", ascending=False)

    if st.session_state.get("PO_df"):
        out_df = st.session_state.PO_df
    else:
        out_df = df.groupby("PAYEE").mean(numeric_only=True).reset_index().sort_values(by="ACTUAL", ascending=False)
        out_df.insert(0, 'DIVE', False)
        out_df.COUNT = out_df.COUNT.astype(int)
    
    changed = st_df(
        out_df, editable=True, use_container_width=True, hide_index=True, disabled=out_df.columns[1:], key="PO_DE_" + st.session_state.session,
        column_config=st.column_config.CheckboxColumn(
            "DIVE", width="small", help="CHECK A BOX TO DISPLAY THAT PAYEE'S PROJECTS"
        )
    )

    if not changed.equals(out_df):
        df = PO[["PAYEE", "ACTUAL", "DATE", "PROJECT NAME", "SECTION", "LINE", "LINE DESCRIPTION"]]
        payee = changed[changed["DIVE"]==True].PAYEE
        st_df(
            df[df.PAYEE.isin(payee)].sort_values(by="PAYEE"),
            use_container_width=True, hide_index=True
        )

def payroll(PR):
    df = PR[["PAYEE", "ACTUAL", "VARIANCE", "VARIANCE (%)", "PROJECT NAME"]]
    counts = df.groupby("PAYEE").size().reset_index(name='COUNT')
    df = pd.merge(df, counts, on="PAYEE").sort_values(by="ACTUAL", ascending=False)
    if st.session_state.get("PR_df"):
        out_df = st.session_state.PR_df
    else:
        out_df = df.groupby("PAYEE").mean(numeric_only=True).reset_index().sort_values(by="ACTUAL", ascending=False)
        out_df.insert(0, 'DIVE', False)
        out_df.COUNT = out_df.COUNT.astype(int)
        out_df["VARIANCE (%)"] = out_df["VARIANCE (%)"].round(2)
    
    out_df.drop(columns=["ACTUAL"], inplace=True)
    changed = st_df(
        out_df, keep_percent=True, editable=True, use_container_width=True, hide_index=True, disabled=out_df.columns[1:], key="PR_DE_" + st.session_state.session,
        column_config={
            "DIVE" : st.column_config.CheckboxColumn(
                "DIVE", width="small", help="CHECK A BOX TO DISPLAY THAT PAYEE'S PROJECTS"
            )
        }
    )

    if not changed.equals(out_df):
        df = PR[["PAYEE", "EST", "ACTUAL", "VARIANCE", "VARIANCE (%)",  "PROJECT NAME", "SECTION", "LINE", "LINE DESCRIPTION"]]
        payee = changed[changed["DIVE"]==True].PAYEE
        st_df(
            df[df.PAYEE.isin(payee)].sort_values(by="PAYEE"), keep_percent=True,
            use_container_width=True, hide_index=True
        )
