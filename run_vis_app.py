from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

from app_utils.auth import USERNAME, PASSWORD, KEY
from app_utils.sql_integration import get_devices_from_database
from app_utils.logs_integration import get_logs

import logging
import glob

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = KEY

# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


@app.route("/", methods=["GET", "POST"])
def login():
    logging.info(f"Accessing login page")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("map_view"))

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():
    logging.info(f"User logged out")
    session.clear()
    return redirect(url_for("login"))


# ------------------------------------------------------------------
# Map
# ------------------------------------------------------------------

@app.route("/map")
@login_required
def map_view():
    logging.info(f"Accessing map view with database: {DATABASE_NAME}")
    return render_template(
        "map.html",
        devices=get_devices_from_database(DATABASE_NAME),
    )

# ------------------------------------------------------------------
# Log Viewer (SERVER)
# ------------------------------------------------------------------

@app.route("/logs")
@login_required
def logs_view():
    logging.info(f"Accessing logs from file: {SERVER_LOG_NAME}")
    return render_template(
        "logs.html",
        devices=get_logs(SERVER_LOG_NAME),
    )

# ------------------------------------------------------------------
# Log Viewer (APP)
# ------------------------------------------------------------------

@app.route("/logs-vis")
@login_required
def logs_view_vis():
    logging.info(f"Accessing logs from file: {LOG_NAME}")
    return render_template(
        "logs.html",
        devices=get_logs(LOG_NAME),
    )

if __name__ == "__main__":
    
    
    LOG_NAME = "vis.log"
    DB_NAME = "database.db"
    logging.basicConfig(filename=LOG_NAME, encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    DATABASE_NAME = "database.db"
    SERVER_LOG_NAME = "server.log"
    try:
        logging.info(f"Starting Flask app with database: {DATABASE_NAME} and log file: {SERVER_LOG_NAME}")
        app.run(
            host="0.0.0.0",
            port=8080,
            debug=True
        )
    except Exception as e:
        logger.error(f"Error running the Flask app: {e}")