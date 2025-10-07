# WiT Fingerprint Dashboard

A web-based fingerprint sensor interface built with Arduino and Flask, designed for **cyber awareness education**.  
This project allows enrolling, searching, deleting fingerprints, and associates each fingerprint with a user name. It also includes a web dashboard with live logs and a database view.

---

## 🎯 Purpose & Use Case

This project is built for **cyber awareness / security education** to demonstrate biometric authentication. It helps users understand concepts such as:
- fingerprint scanning and template storage  
- user identity mapping (ID + name)  
- real-time logging of sensor operations  
- web interfaces interacting with hardware  
- risks and best practices around biometric systems (e.g. template deletion, replay, spoofing, etc.)

---

## 🧰 Components & Requirements

### Hardware
- Arduino Uno R3  
- Fingerprint sensor module (e.g. Adafruit optical sensor)  
- Jumper wires  
- USB cable  

### Software & Libraries
- Arduino IDE  
- Adafruit Fingerprint Sensor Library  
- Python 3  
- Flask  
- PySerial  

---

## 🚀 Setup Instructions

1. **Clone this repository**  
   ```bash
   git clone https://github.com/rein-desu999/fingerprint.git
   cd fingerprint
Install Python dependencies

python3 -m pip install flask pyserial


Upload Arduino sketch

Open the Arduino .ino in Arduino IDE

Install the Adafruit Fingerprint library

Wire the fingerprint sensor (sensor VIN → 5V, GND → GND, TX → Arduino pin 2, RX → Arduino pin 3)

Upload the sketch

Set the serial port in app.py
In app.py, update the line:

SERIAL_PORT = "/dev/tty.usbmodem101"


to match the port your Arduino uses (check via ls /dev/tty.*).

Run the Flask web app

python3 app.py


Open a browser at http://localhost:5000/.

Use the web dashboard

On the Control Panel tab, you can enroll, search, or delete a fingerprint by entering an ID and a name

On the Database tab, you can see all enrolled users, edit names inline, and delete records
