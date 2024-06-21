import time

from gevent import monkey

from Cup import Cup

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

cups: dict[str, Cup] = {}

current_game_state = 'waiting'


# Serial communication function
def read_serial(port, baudrate):
    initial_time = time.time()
    try:
        ser = serial.Serial(port, baudrate, timeout=0)
        print(f"Listening on {port} at {baudrate} baud rate.")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').rstrip()
                if line:
                    # print(f"Received from serial: {line}")
                    data_queue.put(line)

            if time.time() - initial_time > 0.1:
                handle_data(ser)
                initial_time = time.time()

    except serial.SerialException as e:
        print(f"Serial exception: {e}")
    except KeyboardInterrupt:
        print("Exiting serial thread.")
    finally:
        if ser.is_open:
            ser.close()
            print("Serial port closed.")


def handle_data(ser):
    handled = 0
    thrown_away = 0
    while not data_queue.empty():
        data = data_queue.get()
        handled += 1
        # Process the data
        # print(f"Handling data: {data}")
        if "]" in data and "[" in data:
            handle_message(data, ser)
        else:
            thrown_away += 0.5
    # print(f"handled {handled} datapoints, threw {int(thrown_away)} datapoints away :(")


def handle_message(message: str, ser):
    message = message[1:-1].split(", ")
    try:
        cup_id, brightness, z_acceleration = [message[0], int(message[1]), float(message[2])]
    except Exception:
        print("something went wrong dont worry")
        return
    if cup_id not in cups:
        cups[cup_id] = Cup(cup_id, "green", f"Cup {int(cup_id)}", brightness, socketio, ser)
        print(f"registering cup {cup_id}...")
    else:
        if cup_id == "1":
            print(brightness, z_acceleration)
        # print(f"updating cup {cup_id}...")
        cups[cup_id].update(brightness, z_acceleration, current_game_state)


# SocketIO event for a new connection
@socketio.on('connect')
def test_connect():
    print("someone connected!")
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
