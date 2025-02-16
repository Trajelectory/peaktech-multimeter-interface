import logging
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO
import threading
import requests
import time

# Global variables
flask_app = Flask(__name__)
socketio = SocketIO(flask_app, cors_allowed_origins="*")
shared_data = {"value": "--", "unit": "", "status": ""}
flask_server_thread = None  # Declare the global variable
flask_running = False  # Control flag for Flask server

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PeakTech 2025 Widget</title>
    <style>
        body {
            background-color: transparent;
            font-family: 'Digital-7', sans-serif;
            color: #0078D7;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .widget {
            text-align: center;
        }
        .value {
            font-size: 96px;
            margin: 0;
        }
        .unit {
            font-size: 96px;
            margin: 0;
        }
        .status {
            font-size: 24px;
            margin: 0;
            color: #555555;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.0/socket.io.js"></script>
    <script>
        const socket = io();
        socket.on('update', function(data) {
            document.querySelector('.value').textContent = data.value;
            document.querySelector('.unit').textContent = data.unit;
            document.querySelector('.status').textContent = data.status;
        });
    </script>
</head>
<body>
    <div class="widget">
        <span class="value">{{ value }} </span>
        <span class="unit">{{ unit }}</span>
        <p class="status">{{ status }}</p>
    </div>
</body>
</html>
"""
def decode(line):
    result = {}

    if len(line) != 14:
        logging.warning("Invalid byte stream input (wrong length %d)", len(line))
        return result

    try:
        sign = chr(line[0])
        digits = line[1:5].decode()
        decpos = int(chr(line[6]))
        status_byte_1 = line[7]
        status_byte_2 = line[8]
        status_byte_3 = line[9]
        status_byte_4 = line[10]
        bar_graph = line[11]
    except (IndexError, UnicodeDecodeError) as ex:
        logging.warning("Invalid line (%s)", ex)
        return result

    # Decode statuses
    status = []
    if status_byte_1 & (2 ** 0): status.append("BPN")
    if status_byte_1 & (2 ** 1): status.append("HOLD")
    if status_byte_1 & (2 ** 2): status.append("REL")
    if status_byte_1 & (2 ** 3): status.append("AC")
    if status_byte_1 & (2 ** 4): status.append("DC")
    if status_byte_1 & (2 ** 5): status.append("AUTO")
    if status_byte_2 & (2 ** 2): status.append("BATT")
    if status_byte_2 & (2 ** 3): status.append("APO")
    if status_byte_2 & (2 ** 4): status.append("MIN")
    if status_byte_2 & (2 ** 5): status.append("MAX")

    # Decode unit and mode
    unit = ""
    if status_byte_3 & (2 ** 4): unit = "M"
    if status_byte_3 & (2 ** 5): unit = "k"
    if status_byte_3 & (2 ** 6): unit = "m"
    if status_byte_3 & (2 ** 7): unit = "µ"
    mode = None
    if status_byte_4 & (2 ** 0): mode = "°F"
    if status_byte_4 & (2 ** 1): mode = "°C"
    if status_byte_4 & (2 ** 2): mode = "F"
    if status_byte_4 & (2 ** 3): mode = "Hz"
    if status_byte_4 & (2 ** 4): mode = "hFE"
    if status_byte_4 & (2 ** 5): mode = "Ω"
    if status_byte_4 & (2 ** 6): mode = "A"
    if status_byte_4 & (2 ** 7): mode = "V"

    if mode == "F":
        if status_byte_2 & (2 ** 1): unit = "n"

    if digits == "?0:?":
        value = "OL"
        sign = ""
    else:
        digits_a = list(digits)
        if decpos > 0:
            digits_a.insert(min(decpos, 3), ".")
        value = float("".join(digits_a))

    result = {
        "sign": sign,
        "value": value,
        "unit": f"{unit}{mode}".strip(),
        "status": status,
    }
    return result

@flask_app.route("/")
def widget():
    return render_template_string(HTML_TEMPLATE, value=shared_data["value"], unit=shared_data["unit"])

def run_flask_socketio():
    """Run the SocketIO server in a loop."""
    global flask_running
    logging.info("SocketIO server running...")
    socketio.run(flask_app, host="127.0.0.1", port=5000, debug=False)
    logging.info("SocketIO server stopped.")

def start_flask_server():
    """Start the Flask SocketIO server in a separate thread."""
    global flask_server_thread, flask_running
    if not flask_running:
        flask_running = True
        flask_server_thread = threading.Thread(target=run_flask_socketio, daemon=True)
        flask_server_thread.start()
        logging.info("Flask server started.")

def stop_flask_server():
    """Stop the Flask SocketIO server."""
    global flask_running, flask_server_thread
    if flask_running:
        logging.info("Stopping Flask server...")
        flask_running = False
        # SocketIO doesn't stop automatically; this is a placeholder for custom handling.
        if flask_server_thread and flask_server_thread.is_alive():
            flask_server_thread.join(timeout=1)
            logging.info("Flask server thread stopped.")