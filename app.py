from flask import Flask, render_template, request, jsonify
import serial
import threading
import time
import json
import os

SERIAL_PORT = "/dev/tty.usbmodem101"
BAUD_RATE = 9600

# Initialize serial
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

app = Flask(__name__)
arduino_logs = []
DATA_FILE = "data.json"

# Load existing user data
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def read_serial():
    while True:
        if ser.in_waiting:
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    arduino_logs.append(line)
                    if len(arduino_logs) > 200:
                        arduino_logs.pop(0)
            except Exception as e:
                print("Serial read error:", e)
        time.sleep(0.05)

threading.Thread(target=read_serial, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/command", methods=["POST"])
def command():
    cmd = request.json.get("cmd")
    id_value = request.json.get("id")
    name_value = request.json.get("name")

    if cmd == "1" and id_value:
        # Add to database before enrolling
        users = load_data()
        if not any(u["id"] == id_value for u in users):
            users.append({"id": id_value, "name": name_value, "image": "static/fingerprint.png"})
            save_data(users)
        ser.write(f"1,{id_value}\n".encode())
    elif cmd == "2":
        ser.write(b"2\n")
    elif cmd == "3" and id_value:
        # Remove from database
        users = load_data()
        users = [u for u in users if u["id"] != id_value]
        save_data(users)
        ser.write(f"3,{id_value}\n".encode())
    else:
        return jsonify({"error": "Invalid command"}), 400

    ser.flush()
    return jsonify({"status": "sent"})

@app.route("/logs")
def logs():
    return jsonify({"logs": arduino_logs[-100:]})

@app.route("/users")
def users():
    return jsonify(load_data())

if __name__ == "__main__":
    app.run(debug=True)
# To run the app, use the command: python app.py