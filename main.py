import time

from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

cup_states = ['white', 'red', 'green']
game_states = ['waiting', 'countdown', 'running']

cups = {}

def start_game2():
    time.sleep(5)
    emit('cup_state', {'data' : [{'id': 1, 'color': 'red'}, {'id': 2, 'color': 'green'}, {'id': 3, 'color': 'white'}]})
    print("Game started")

@app.route('/')
def index():
    return "WebSocket Server von TaserCup"

@app.route('/register')
def register_cup():
    #get ip addr of cup
    #store ip addr in cups dict
    cop_ip = request.remote_addr
    cups[cop_ip] = {'id': request.remote_addr, 'color': 'white'}
    print(cups)
    return "Register Cup"

@socketio.on('connect')
def test_connect():
    emit('after connect', {'data': 'Connected'})

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    emit('response', {'data': data})

# on identify

@socketio.on('game_start')
def start_game(data):
    print('received game_start: ' + data)
    emit('response', {'data': 'Game started'})
    start_game2()

def reset_game():
    print('Game reset')
    emit('reset', {'data': 'Game reset'})

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
