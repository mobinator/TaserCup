import serial
import threading
import queue
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

# Thread-safe Queue for communication between threads
data_queue = queue.Queue()


# Serial communication function
def read_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=0)
        print(f"Listening on {port} at {baudrate} baud rate.")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').rstrip()
            if line:
                print(f"Received from serial: {line}")
                data_queue.put(line)

    except serial.SerialException as e:
        print(f"Serial exception: {e}")
    except KeyboardInterrupt:
        print("Exiting serial thread.")
    finally:
        if ser.is_open:
            ser.close()
            print("Serial port closed.")


# Route to get data from the serial thread
@app.route('/get_data', methods=['GET'])
def get_data():
    data_list = []
    while not data_queue.empty():
        data_list.append(data_queue.get())
    return jsonify(data_list)


# Route to send data to the serial port
@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json.get('data')
    if data:
        # Here you would send the data to the serial port if needed
        print(f"Data to send to serial: {data}")
        return jsonify({"status": "success", "data": data})
    return jsonify({"status": "error", "message": "No data provided"}), 400


def start_serial_thread():
    port = "COM9"
    baudrate = 115200
    serial_thread = threading.Thread(target=read_serial, args=(port, baudrate))
    serial_thread.daemon = True
    serial_thread.start()


if __name__ == "__main__":
    start_serial_thread()
    app.run(host='0.0.0.0', port=5000)
