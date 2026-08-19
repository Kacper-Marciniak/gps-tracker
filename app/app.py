from dash import Dash, dcc, html, callback_context, no_update
from dash.dependencies import Input, Output, State
from dash_bootstrap_components import themes
import dash_auth

from functools import wraps

from app.auth.auth import VALID_USERNAME_PASSWORD_PAIRS, SECRET_KEY
from app.layout.base import servePage
from app.layout.page_gps import serveGPScontent, updateMap, getDevicesLocation
from app.layout.page_logs import serveLogsContent

import logging

logger = logging.getLogger(__name__)

app = Dash(__name__,
    external_stylesheets =[themes.LITERA],
    suppress_callback_exceptions=True,
    title = "GPS Tracker",
    update_title='...',
)
app._favicon = r'app.png'

auth = dash_auth.BasicAuth(
    app,
    username_password_list = VALID_USERNAME_PASSWORD_PAIRS,
    secret_key=SECRET_KEY
)

def _serve_layout():
    return html.Div([
        html.Meta(charSet="utf-8"),
        dcc.Location(id='url', refresh=True),
        html.Div(id='page'),
    ])

# Update displayed page
@app.callback(
    Output('page', 'children'),
    Input('url', 'pathname')
)
def display_page(sUrl: str | None):
    if sUrl == "/" or sUrl == "/gps" or sUrl == "/map":
        return servePage(lContent=serveGPScontent(), sTitle="GPS Tracker")
    if sUrl == "/logs":
        return servePage(lContent=serveLogsContent(), sTitle="GPS Tracker")
    else:
        return no_update
    
app.layout = _serve_layout()

########################
# CALLBACKS - GPS PAGE #
########################

# Update displayed page
@app.callback(
    Output("gps-markers-layer", "children"),
    Output("gps-trace-layer", "children"),

    Input("gps-trace-update-map-button", "n_clicks"),

    State("gps-trace-device-dropdown", "value"),
    State("gps-trace-date-range", "start_date"),
    State("gps-trace-date-range", "end_date"),
)
def callback_update_map(
    iNClicks: int | None,
    sDevice: str | None,
    sStartDate: str | None,
    sEndDate: str | None,
):
    if callback_context.triggered_id == "gps-trace-update-map-button":
        lMarkers, lTraces = updateMap(iNClicks, sDevice, sStartDate, sEndDate)
    else:
        lMarkers = getDevicesLocation()
        lTraces = no_update

    return lMarkers, lTraces