from flask import Flask, render_template, request, jsonify
import serial
import threading
import time
import json
import os
import re

app = Flask(__name__)

SERIAL_PORT = "/dev/tty.usbmodem101"  # Update if needed
BAUD_RATE = 9600
SEARCH_TIMEOUT = 3  # seconds

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
logs = []
db_file = "data.json"
lock = threading.Lock()

# Load database
if os.path.exists(db_file):
    with open(db_file, "r") as f:
        database = json.load(f)
else:
    database = []

# Helper: append log
def append_log(msg):
    with lock:
        logs.append(msg)
        print(msg)

# Background thread to read serial
arduino_buffer = []
def read_serial():
    global arduino_buffer
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                arduino_buffer.append(line)
                append_log(line)
        time.sleep(0.01)

threading.Thread(target=read_serial, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/database")
def database_page():
    return render_template("database.html", users=database)


@app.route("/command", methods=["POST"])
def command():
    data = request.get_json()
    cmd = data.get("cmd")
    fid = data.get("id")
    name = data.get("name", "")

    if cmd == "1":  # Enroll
        if not fid or not name:
            append_log("❌ Please enter both ID and Name to enroll.")
            return jsonify(success=False)
        # Check if ID already exists
        if any(d["id"] == fid for d in database):
            append_log(f"❌ ID {fid} already taken. Choose another.")
            return jsonify(success=False)

        append_log(f"🟣 Enrolling ID {fid} ({name})...")
        database.append({"id": fid, "name": name})
        with open(db_file, "w") as f:
            json.dump(database, f, indent=2)
        ser.write(f"{cmd},{fid}\n".encode())

        # Wait for confirmation from Arduino
        start = time.time()
        confirmed = False
        while time.time() - start < 5:  # 5 sec timeout
            while arduino_buffer:
                line = arduino_buffer.pop(0)
                if f"Fingerprint ID #{fid} stored successfully" in line:
                    append_log(f"✅ Enrollment confirmed for ID {fid} ({name})")
                    confirmed = True
                    break
            if confirmed:
                break
            time.sleep(0.05)
        if not confirmed:
            append_log(f"❌ Enrollment timeout for ID {fid}")

    elif cmd == "2":  # Search
        append_log("🔍 Searching for fingerprint...")
        ser.write(f"{cmd}\n".encode())
        start = time.time()
        found = False
        while time.time() - start < SEARCH_TIMEOUT:
            while arduino_buffer:
                line = arduino_buffer.pop(0)
                if "Match found! ID:" in line:
                    fid_match = re.search(r"ID: (\d+)", line).group(1)
                    name_match = next((u["name"] for u in database if u["id"] == fid_match), "Unknown")
                    append_log(f"✅ Match found: ID={fid_match} | Name={name_match}")
                    found = True
                    break
                elif "No match found" in line:
                    append_log("❌ No match found")
                    found = True
                    break
            if found:
                break
            time.sleep(0.05)
        if not found:
            append_log("❌ No match found (timeout)")

    elif cmd == "3":  # Delete
        if not fid:
            append_log("❌ Please enter ID to delete.")
            return jsonify(success=False)
        if not any(d["id"] == fid for d in database):
            append_log(f"❌ ID {fid} not found in database.")
            return jsonify(success=False)

        # Remove locally
        database[:] = [d for d in database if d["id"] != fid]
        with open(db_file, "w") as f:
            json.dump(database, f, indent=2)
        # Send delete to Arduino
        ser.write(f"{cmd},{fid}\n".encode())
        append_log(f"🗑️ Deleted ID {fid} from database and sent command to Arduino.")

    return jsonify(success=True)


@app.route("/logs")
def get_logs():
    with lock:
        return jsonify({"logs": logs[-50:]})  # last 50 logs


@app.route("/clear_logs", methods=["POST"])
def clear_logs():
    with lock:
        logs.clear()
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# To run: python app.py