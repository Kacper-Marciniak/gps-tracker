import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, callback_context, no_update

import dash_bootstrap_components as dbc
from dash import html


def serveNavbar(sTitle: str):
    return dbc.Navbar(
        html.Div(
            [
                # Left
                html.Div(
                    [
                        html.A(
                            html.Img(
                                src="/assets/logo_pwr.png",
                                alt="Wrocław University of Science and Technology",
                                className="navbar-logo",
                            ),
                            href="https://www.pwr.edu.pl/",
                            className="logo-navbar",
                        ),

                        html.A(
                            html.Img(
                                src="/assets/logo_mvlab.png",
                                alt="MVLab",
                                className="navbar-logo",
                            ),
                            href="https://www.mvlab.pl/",
                            className="logo-navbar",
                        ),
                    ],
                    className="navbar-left",
                ),

                # Center
                html.Div(
                    [
                        html.H1(
                            sTitle,
                            className="navbar-title",
                        ),

                        html.Img(
                            src="/assets/app_shadow.png",
                            alt="",
                            className="navbar-app-logo",
                        ),
                    ],
                    className="navbar-center",
                ),

                # Right
                html.Div(
                    html.A(
                        html.Img(
                            src="/assets/logo_github.png",
                            alt="GitHub",
                            className="navbar-logo",
                        ),
                        href="https://github.com/Kacper-Marciniak",
                        className="logo-navbar",
                    ),
                    className="navbar-right",
                ),
            ],
            className="navbar-container",
        ),
        className="app-navbar",
        sticky="top",
    )


def serveFooter():
    return html.Footer(
        html.Div(
            [
                html.P(
                    "Machine Vision and Laser Laboratory",
                    className="footer-text",
                ),
                html.P(
                    "2026",
                    className="footer-text",
                ),
            ],
            className="footer-content",
        ),
        className="app-footer",
    )


def servePage(lContent: list, sTitle: str):
    return html.Div(
        [
            serveNavbar(sTitle),

            html.Main(
                lContent,
                className="app-content",
            ),

            serveFooter(),
        ],
        className="page-wrapper",
    )
