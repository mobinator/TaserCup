from gevent import monkey

monkey.patch_all()

import serial
import threading
import queue
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

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
                # print(f"Received from serial: {line}")
                data_queue.put(line)
                socketio.emit('serial_data', {'data': line})  # Emit data to SocketIO clients

    except serial.SerialException as e:
        print(f"Serial exception: {e}")
    except KeyboardInterrupt:
        print("Exiting serial thread.")
    finally:
        if ser.is_open:
            ser.close()
            print("Serial port closed.")

# SocketIO event for a new connection
@socketio.on('connect')
def test_connect():
    print("Someone connected!")
    emit('after connect', {'data': 'Connected'})


def start_serial_thread():
    port = "COM9"
    baudrate = 115200
    serial_thread = threading.Thread(target=read_serial, args=(port, baudrate))
    serial_thread.daemon = True
    serial_thread.start()


if __name__ == "__main__":
    start_serial_thread()
    socketio.run(app, host='0.0.0.0', port=5000)
