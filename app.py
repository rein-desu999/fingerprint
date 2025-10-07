from flask import Flask, render_template, request, jsonify
import serial
import threading
import time
import json
import os

app = Flask(__name__)

SERIAL_PORT = "/dev/tty.usbmodem101"  # Update if needed
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
logs = []
db_file = "data.json"
lock = threading.Lock()

# Load or create the local "database"
if os.path.exists(db_file):
    with open(db_file, "r") as f:
        database = json.load(f)
else:
    database = []


# Background thread to read serial logs
def read_serial():
    global logs
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                with lock:
                    logs.append(line)
                print(line)


thread = threading.Thread(target=read_serial, daemon=True)
thread.start()


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
        if fid and name:
            database.append({"id": fid, "name": name})
            with open(db_file, "w") as f:
                json.dump(database, f, indent=2)
            ser.write(f"{cmd},{fid}\n".encode())
            logs.append(f"🟣 Enrolling ID {fid} ({name})...")
        else:
            logs.append("❌ Please enter both ID and Name to enroll.")

    elif cmd == "2":  # Search
        ser.write(f"{cmd}\n".encode())
        logs.append("🔍 Searching for fingerprint...")
        # Mocked result for display purposes
        time.sleep(1)
        for user in database:
            logs.append(f"✅ Match found: ID={user['id']} | Name={user['name']}")

    elif cmd == "3":  # Delete
        if fid:
            database[:] = [d for d in database if d["id"] != fid]
            with open(db_file, "w") as f:
                json.dump(database, f, indent=2)
            ser.write(f"{cmd},{fid}\n".encode())
            logs.append(f"🗑️ Deleted ID {fid}")
        else:
            logs.append("❌ Please enter ID to delete.")

    return jsonify(success=True)


@app.route("/update_user", methods=["POST"])
def update_user():
    data = request.get_json()
    uid = data.get("id")
    new_name = data.get("name")

    for user in database:
        if user["id"] == uid:
            user["name"] = new_name
            with open(db_file, "w") as f:
                json.dump(database, f, indent=2)
            logs.append(f"✏️ Updated name for ID {uid} → {new_name}")
            return jsonify(success=True)
    return jsonify(success=False), 404


@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    uid = data.get("id")

    before_count = len(database)
    database[:] = [u for u in database if u["id"] != uid]
    after_count = len(database)

    with open(db_file, "w") as f:
        json.dump(database, f, indent=2)

    if before_count != after_count:
        logs.append(f"🗑️ Deleted user ID {uid} via dashboard.")
        ser.write(f"3,{uid}\n".encode())
        return jsonify(success=True)
    return jsonify(success=False), 404


@app.route("/logs")
def get_logs():
    with lock:
        return jsonify({"logs": logs[-50:]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# To run: python app.py