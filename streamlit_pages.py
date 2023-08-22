from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import theme


METRICS = ["VARIANCE", "VARIANCE (%)", "ESTIMATE", "ACTUAL"]


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

def highlight(row, to_highlight):
    if any(item in to_highlight for item in row.values):
        return [f'background-color: {theme.SECONDARY_COLOR}; color:{theme.BG_COLOR_SECONDARY}'] * len(row)
    else:
        return [''] * len(row)


# PAGES —————————————————————————————————————————————————————————————————————————————————————————————————————————
def home():
    add_v_space(2)
    st.image(theme.logo_img)
    with st.empty():
        cols = st.columns(3)
        with cols[1]:
            st.markdown("### PRODUCTION BUDGET ANALYSIS")
            
    add_v_space(8)
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
            display_df = df["VARIANCE"].reset_index(drop=False)
            if st.session_state.get("cs_sel_section"):
                check_df = CSSS[CSSS["SECTION"].isin(st.session_state.cs_sel_section)]
                if not check_df.empty:
                    display_df = display_df.style.apply(highlight, axis=1, to_highlight=st.session_state.cs_sel_section)
            st.dataframe(display_df, use_container_width=True, height=550, hide_index=True)
        with cols[1]:
            if st.session_state.get("cs_sel_section"):
                if not check_df.empty:
                    CSSS = check_df
                st.markdown("#### {} SECTION(S) AVERAGE METRICS".format(", ".join(st.session_state.cs_sel_section)))
            else:
                st.markdown("#### ALL SECTIONS AVERAGE METRICS")
            
            avgs = CSSS[METRICS].mean().to_frame().T
            st.dataframe(avgs, hide_index=True, use_container_width=True)
            with st.empty():
                create_sel_bar_plot(df)

    
    st.markdown("### AVERAGE VARIANCE BY SUBSECTION")
    st.divider()
    
    with st.container():
        df = CSSS.groupby("SUB SECTION").mean(numeric_only=True).sort_values(by="VARIANCE", ascending=False)
        
        cols = st.columns([0.3, 0.7])
        with cols[0]:
            st.dataframe(df[["VARIANCE", "VARIANCE (%)"]], use_container_width=True)
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
            st.dataframe(df[["VARIANCE", "VARIANCE (%)"]], use_container_width=True)
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
        df_to_show['SECTION'] = df_to_show['SECTION'].mask(df_to_show['SECTION'].duplicated(), '')
    else:
        df_to_show = df_to_show.groupby("SECTION").mean(numeric_only=True).reset_index()


    st.dataframe(df_to_show, use_container_width=True, hide_index=True)


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
    
    changed = st.data_editor(
        out_df, use_container_width=True, hide_index=True, disabled=out_df.columns[1:], key="PO_DE_" + st.session_state.session,
        column_config=st.column_config.CheckboxColumn(
            "DIVE", width="small", help="CHECK A BOX TO DISPLAY THAT PAYEE'S PROJECTS"
        )
    )

    if not changed.equals(out_df):
        payee = changed[changed["DIVE"]==True].PAYEE
        st.dataframe(
            df[df.PAYEE.isin(payee)].sort_values(by="PAYEE"),
            use_container_width=True, hide_index=True
        )

