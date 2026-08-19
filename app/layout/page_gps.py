from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from datetime import datetime, timezone, timedelta
from app.integration.sql import get_devices_from_database, get_device_traces, get_device_location


def serveGPScontent() -> list:
    dcDevices = get_devices_from_database()
    sCurrentDate = datetime.now().strftime("%Y-%m-%d")
    sDayBefore = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    return [html.Div(
        [
            # ========================================
            # MAP
            # ========================================
            dl.Map(
                [
                    dl.TileLayer(
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                        attribution=(
                            '&copy; <a href="https://www.openstreetmap.org/copyright">'
                            "OpenStreetMap contributors</a>"
                        ),
                    ),

                    dl.LayerGroup(
                        id="gps-markers-layer",
                    ),

                    dl.LayerGroup(
                        id="gps-trace-layer",
                    ),
                ],
                id="gps-map",
                className="gps-map-container",
                center=[51.1079, 17.0385],
                zoom=13,
            ),
            
            # ========================================
            # TOP CONTROL BAR
            # ========================================
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            
                        ],
                        title="...",
                    ),
                    dbc.AccordionItem(
                        [
                            html.Div(
                                [
                                    # Device selector
                                    html.Div(
                                        [
                                            html.H4(
                                                "Device",
                                                className="control-label",
                                            ),
                        
                                            dcc.Dropdown(
                                                id="gps-trace-device-dropdown",
                                                options=dcDevices,
                                                value=dcDevices[0]["value"] if dcDevices else None,
                                                placeholder="Select device...",
                                                clearable=False,
                                                className="gps-device-dropdown",
                                            ),
                                        ],
                                        className="gps-control-device",
                                    ),
                        
                                    # Date/time range
                                    html.Div(
                                        [
                                            html.H4(
                                                "Date range",
                                                className="control-label",
                                            ),
                        
                                            dcc.DatePickerRange(
                                                id="gps-trace-date-range",
                                                start_date=sDayBefore,
                                                end_date=sCurrentDate,
                                                display_format="YYYY-MM-DD",
                                                className="gps-date-range",
                                            ),
                                        ],
                                        className="gps-control-date",
                                    ),
                        
                                    # Button to update the map
                                    html.Div(
                                        [
                                            dbc.Button(
                                                "Update Map",
                                                color="secondary",
                                                id="gps-trace-update-map-button",
                                                n_clicks=0,
                                                className="gps-update-map-button",
                                            ),
                                        ],
                                        className="gps-control-button",
                                    ),
                                ],
                                className="gps-controls-trace",
                            ),
                        ],
                        title="Trace Controls",
                    )
                ],
                className="gps-controls-accordion",
            ),
        ],
        className="gps-map-wrapper",
    )]

########################
# CALLBACKS - GPS PAGE #
########################

def getDevicesLocation(
):
    dcDevices = get_devices_from_database()
    lGPSData = []
    for device in dcDevices:
        sDeviceID = device["value"]
        dcGPSData = get_device_location(device_id=int(sDeviceID))
        if dcGPSData:
            lGPSData.append(dcGPSData)
    
    if not lGPSData:
        return []

    # ========================================
    # GPS POINTS
    # ========================================

    lMarkers = []

    for i,dPoint in enumerate(lGPSData):

        fLatitude = dPoint["latitude"]
        fLongitude = dPoint["longitude"]

        cPop = dl.Popup(
            html.Div(
                [
                    html.B(f"ID: {dPoint['device_id']}"),
                    html.Br(),
                    html.P(f"Time: {dPoint['datetime']}"),
                    html.P(f"Latitude: {fLatitude:.6f}"),
                    html.P(f"Longitude: {fLongitude:.6f}"),
                    html.P(f"Speed: {dPoint['speed']:.1f}km/h"),
                    html.P(f"Battery: {dPoint['battery']:d}%"),
                ],
                className="gps-popup",
            )
        )

        lMarkers.append(dl.Marker(
            position=[
                fLatitude,
                fLongitude,
            ],
            children=[cPop],
        ))

    return lMarkers


def updateMap(
    iNClicks: int | None,
    sDevice: str | None,
    sStartDate: str | None,
    sEndDate: str | None,
):
    if sDevice is None or sStartDate is None or not iNClicks:
        return [], []

    # Load GPS data
    sStartDate = datetime.strptime(sStartDate, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
    sEndDate = datetime.strptime(sEndDate, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59") if sEndDate else None
    lGPSData = get_device_traces(device_id=int(sDevice), date_range=(sStartDate, sEndDate))

    if not lGPSData:
        return [], []

    # ========================================
    # GPS POINTS
    # ========================================

    lMarkers = []

    for i,dPoint in enumerate(lGPSData):

        fLatitude = dPoint["latitude"]
        fLongitude = dPoint["longitude"]

        cPop = dl.Popup(
            html.Div(
                [
                    html.B("GPS Point"),
                    html.Br(),
                    html.P(f"Time: {dPoint['datetime']}"),
                    html.P(f"Latitude: {fLatitude:.6f}"),
                    html.P(f"Longitude: {fLongitude:.6f}"),
                    html.P(f"Speed: {dPoint['speed']:.1f} km/h"),
                ],
                className="gps-popup",
            )
        )

        if i != 0:
            lMarkers.append(dl.CircleMarker(
                center=[
                    fLatitude,
                    fLongitude,
                ],
                radius=6,
                fillOpacity=0.0,
                opacity=0.0,
                children=[cPop],
            ))

            lMarkers.append(dl.CircleMarker(
                center=[
                    fLatitude,
                    fLongitude,
                ],
                radius=1,
                color="blue",
                fillColor="blue",
                children=[cPop],
            ))
        else:
            lMarkers.append(dl.Marker(
                position=[
                    fLatitude,
                    fLongitude,
                ],
                children=[cPop],
            ))

    # TRACE

    lPositions = [
        [
            dPoint["latitude"],
            dPoint["longitude"],
        ]
        for dPoint in lGPSData
    ]

    lTrace = dl.Polyline(
        positions=lPositions,
        color="blue",
        weight=5,
        opacity=0.6,
    )

    return lMarkers, [lTrace]