import plotly.graph_objects as go
import plotly.io as pio

PRIMARY_COLOR = "#643CDC"
SECONDARY_COLOR = "#E1E6C3"
BG_COLOR_PRIMARY = "#000000"
BG_COLOR_SECONDARY = "#323232"
LINE_COLOR = "#646464"
TEXT_COLOR = "#FFFFFF"

FONT_CHANGE_CSS = '<style>html, body, [class*="css"] {font-family: helvetica, sans-serif;}</style>'

logo_img = "https://github.com/querybila/Automating-ChatGPT-with-Python-and-Selenium/assets/63984796/f3e20841-af08-4139-b686-200a7bccb783"
stamp_img = "https://github.com/querybila/Automating-ChatGPT-with-Python-and-Selenium/assets/63984796/1f833bde-8bc8-47fb-b1b6-9a6a8c1f294f"

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        plot_bgcolor = BG_COLOR_PRIMARY,
        paper_bgcolor = BG_COLOR_PRIMARY,
        font = dict(color=TEXT_COLOR),
        colorway=[
            '#643cdc','#c33cdc','#dc3c93',
            '#dc443c','#dca43c','#b3dc3c',
            '#54dc3c','#3cdc83','#3cd4dc',
            '#3c73dc'
        ],
        xaxis=dict(
            automargin=True,
            gridcolor=LINE_COLOR,
            gridwidth=1,
            zerolinecolor=LINE_COLOR,
            zerolinewidth=1
        ),
        yaxis=dict(
            automargin=True,
            showgrid=True,
            gridcolor=LINE_COLOR,
            gridwidth=1,
            zerolinecolor=LINE_COLOR,
            zerolinewidth=3
        )
    ),
)

template_name = "626_theme"
pio.templates[template_name] = PLOTLY_TEMPLATE
pio.templates.default = template_name