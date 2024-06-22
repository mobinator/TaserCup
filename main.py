import time

from gevent import monkey

from Cup import Cup, cup_states

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

early_starters = []

tasers_active = False

game_start_time = time.time()


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
            if "]" not in data and "[" not in data and "ess" in data:
                print(data)
            thrown_away += 0.5
    # print(f"handled {handled} datapoints, threw {int(thrown_away)} datapoints away :(")


def handle_message(message: str, ser):
    message = message[1:-1].split(", ")
    try:
        cup_id, brightness, z_acceleration = [message[0], int(message[1]), float(message[2])]
    except Exception:
        print("something went wrong dont worry")
        return

    if cup_id not in cups and int(cup_id) >= 0:
        cups[cup_id] = Cup(cup_id, "green", f"Cup {int(cup_id)}", brightness, socketio, ser)
        print(f"registering cup {cup_id}...")
        socketio.emit('all_cups', {'data': [cups[cup].to_json() for cup in cups]})
    elif int(cup_id) < 0:
        pass
    else:
        cups[cup_id].update(brightness, z_acceleration, current_game_state)
        update_game()


game_states = ['waiting', 'countdown', 'running']


def update_game():
    global current_game_state

    if current_game_state == game_states[0]:
        return

    elif current_game_state == game_states[1]:
        print("Counting down")
        for cup in cups.values():
            if cup.safe:
                early_starters.append(cup)

        if time.time() - game_start_time > 2.8:
            current_game_state = game_states[2]

    elif current_game_state == game_states[2]:

        for cup in cups.values():
            if cup.standing_again and not cup.safe:
                cup.safe = True
                cup.update_color('green')

        safe_cup_count = len([cup for cup in cups.values() if cup.safe == False])

        if safe_cup_count == 1:
            current_game_state = game_states[0]
            print("Spiel vorbei")
            if len([cup for cup in cups.values() if cup.color == 'green']) > 0:
                for cup in cups.values():
                    if not cup.safe:
                        cup.activate_taser()
            else:
                for cup in cups.values():
                    if not cup.safe:
                        cup.update_color('green')
            reset_game()


# SocketIO event for a new connection
@socketio.on('connect')
def test_connect():
    print("someone connected!")
    emit('after connect', {'data': 'Connected'})
    emit('all_cups', {'data': [cups[cup].to_json() for cup in cups]})
    reset_game()


@socketio.on('game_start')
def start_game(data):
    global current_game_state, tasers_active, game_start_time, early_starters

    current_game_state = 'countdown'
    tasers_active = True

    # make all cups unsafe
    for cup in cups.values():
        cup.safe = False
        cup.standing_again = False
        cup.color = 'white'
        socketio.emit('cup_state', {'data': cup.to_json()})
        print(cup.to_json())

    print('received game_start: ' + data)

    socketio.emit('game_started', {'data': 'Countdown Started'})

    early_starters = []

    game_start_time = time.time()


def reset_game():
    global current_game_state
    print('Game reset')
    current_game_state = 'waiting'
    for cup in cups.values():
        cup.safe = True
    socketio.emit('reset', {'data': 'Game reset'})


def new_cup(data):
    print('New cup: ', data)
    socketio.emit('new_cup', {'data': data})


def start_serial_thread():
    port = "COM9"
    baudrate = 115200
    serial_thread = threading.Thread(target=read_serial, args=(port, baudrate))
    serial_thread.daemon = True
    serial_thread.start()


if __name__ == "__main__":
    start_serial_thread()
    socketio.run(app, host='0.0.0.0', port=5000)
