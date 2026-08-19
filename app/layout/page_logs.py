from dash import dcc, html
import dash_bootstrap_components as dbc
from app.integration.logs import get_server_logs


def serveLogsContent() -> list:
    lTextLog = get_server_logs(max_lines=1000)
    return [html.Div(
        [
            # ========================================
            # LOGS
            # ========================================
            html.H4("Server Logs", className="logs-title"),
            dcc.Textarea(
                value="\n".join(lTextLog),
                style={"width": "100%", "height": "400px"},
                readOnly=True,
                className="logs-textarea",
            ),
        ],
        className="logs-wrapper",
    )]