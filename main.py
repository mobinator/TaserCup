import eventlet

eventlet.monkey_patch()

import time
import sys
import signal

import Cup

from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_serial import Serial
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config['SERIAL_TIMEOUT'] = 0.1
app.config['SERIAL_PORT'] = 'COM4'
app.config['SERIAL_BAUDRATE'] = 115200
app.config['SERIAL_BYTESIZE'] = 8
app.config['SERIAL_PARITY'] = 'N'
app.config['SERIAL_STOPBITS'] = 1

serial = Serial(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

cup_colors = ['white', 'red', 'green']
cup_states = ['steht', 'wird aufgehoben' , 'trinken', 'wird abgestellt']
game_states = ['waiting', 'countdown', 'running']

current_game_state = 'waiting'

tasers_active = False

cups: dict[int: Cup.Cup] = {}

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

# function to handle incoming Serial data
# also handles the register function
# Sender: 08:D1:F9:CE:FA:90
# Empfänger: 08:D1:F9:CE:FE:3C

@serial.on_message()
def handle_message(msg):

    data = str(msg).replace(r'\r\n', '')[3:-2].split('][')
    messages = [d.split(',') for d in data]
    for message in messages:
        if len(message) < 3:
            continue
        cup_id, brightness, z_acceleration = int(message[0]), int(message[1]), float(message[2])
        if cup_id not in cups:
            register_cup(cup_id, 'Cup ' + str(cup_id), brightness)
        cups[cup_id].update(brightness, z_acceleration, current_game_state)
        # print(cup_id, brightness, z_acceleration)
        # print(message)

def register_cup(cup_id, name, brightness):
    print('Registering cup: ', cup_id)
    cups[cup_id] = Cup.Cup(cup_id, 'white', name, brightness, socketio, serial)
    print('Registered cup: ', cups[cup_id])

@app.route('/')
def index():
    return "WebSocket Server von TaserCup"

@app.route('/message')
def message():
    message_data: str = request.args.get('data')
    print('Message received: ', message_data)
    return "message Received"

@socketio.on('connect')
def test_connect():
    emit('after connect', {'data': 'Connected'})
    emit('all_cups', {'data': [cups[cup].to_json() for cup in cups]})

@socketio.on('game_start')
def start_game(data):
    global current_game_state, tasers_active

    # game_start_time = time.time()

    current_game_state = 'countdown'
    tasers_active = True
    #make all cups unsafe
    for cup in cups.values():
        cup.safe = False
        cup.color = 'white'
        socketio.emit('cup_state', {'data': cup.to_json()})

    print('received game_start: ' + data)

    time.sleep(5)

    print("Game started")
    current_game_state = 'running'
    emit('response', {'data': 'Game started'})

    while tasers_active:
        # Game loop
        # TODO: Implement game logic

        # if only one cup is white, set all cups to safe
        if len([cup for cup in cups.values() if cup.color == 'white']) == 1:
            for cup in cups.values():
                if not cup.safe:
                    cup.activate_taser()
                    cup.update_color('red')

            print('All cups are safe')
            tasers_active = False
            break

        reset_game()

def reset_game():
    print('Game reset')
    emit('reset', {'data': 'Game reset'})

def new_cup(data):
    print('New cup: ', data)
    socketio.emit('new_cup', {'data': data})


if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT, signal_handler)
        socketio.run(app, port=5000, debug=False)
    except KeyboardInterrupt:
        print("Programm beendet.")
    finally:
        sys.exit(0)

