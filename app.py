from flask import Flask, render_template, request, jsonify
import serial
import threading
import time

# Replace with your Arduino port
SERIAL_PORT = "/dev/tty.usbmodem101"
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Wait for Arduino reset

app = Flask(__name__)

# Store last 100 Arduino log messages
arduino_logs = []

# Background thread to read Arduino Serial logs
def read_serial():
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                arduino_logs.append(line)
                # Keep only the last 100 messages
                if len(arduino_logs) > 100:
                    arduino_logs.pop(0)

threading.Thread(target=read_serial, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/command", methods=["POST"])
def command():
    cmd = request.json.get("cmd")
    id_value = request.json.get("id", None)

    # Format command as Arduino expects: "1,5\n", "2\n", etc.
    if id_value:
        full_cmd = f"{cmd},{id_value}\n"
    else:
        full_cmd = f"{cmd}\n"

    ser.write(full_cmd.encode())
    return jsonify({"status": "sent"})

@app.route("/logs")
def logs():
    return jsonify({"logs": arduino_logs})

if __name__ == "__main__":
    app.run(debug=True)
