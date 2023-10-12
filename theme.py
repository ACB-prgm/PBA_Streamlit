import plotly.graph_objects as go
import plotly.io as pio


# COLORS ———————————————————————————————————————————————————————————————————————————————————————————————————
PRIMARY_COLOR = "#643CDC"
SECONDARY_COLOR = "#E1E6C3"
BG_COLOR_PRIMARY = "#000000"
BG_COLOR_SECONDARY = "#323232"
RED = "DB6A51"
GREEN = "30DB9D"

LINE_COLOR = "#646464"
TEXT_COLOR = "#FFFFFF"

def html_to_rgba(color_code):
    # Remove the hash at the start if it's there
    color_code = color_code.lstrip('#')

    # Length of the color code
    length = len(color_code)

    # Convert
    if length == 6:
        r = int(color_code[0:2], 16)
        g = int(color_code[2:4], 16)
        b = int(color_code[4:6], 16)
        a = 255  # Fully opaque
    elif length == 8:
        r = int(color_code[0:2], 16)
        g = int(color_code[2:4], 16)
        b = int(color_code[4:6], 16)
        a = int(color_code[6:8], 16)
    else:
        raise ValueError("Input #color_code should be in the format '#RRGGBB' or '#RRGGBBAA'")

    return r, g, b, a

RED_RGBA = html_to_rgba(RED)
GREEN_RGBA = html_to_rgba(GREEN)

# OTHER ———————————————————————————————————————————————————————————————————————————————————————————————————
FONT_CHANGE_CSS = '<style>html, body, [class*="css"] {font-family: helvetica, sans-serif;}</style>'

# Brand Assets: https://www.dropbox.com/sh/cg533fydy6228t0/AADuyG_xtVpmbiTwviwHwPYYa?dl=0
logo_img = "https://github.com/ACB-prgm/PBA_Streamlit/assets/63984796/667390de-aed6-430e-b57b-9920e4c1715d"
stamp_img = "https://github.com/ACB-prgm/PBA_Streamlit/assets/63984796/399fecc3-4b79-4688-be25-9473d4c00ff9"

# PLOTLY ———————————————————————————————————————————————————————————————————————————————————————————————————
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