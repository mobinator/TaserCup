import time

from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

cup_states = ['white', 'red', 'green']
game_states = ['waiting', 'countdown', 'running']

cups = {}

@app.route('/')
def index():
    return "WebSocket Server von TaserCup"

@app.route('/register')
def register_cup():
    #get ip addr of cup
    #store ip addr in cups dict
    cup_ip = request.remote_addr
    cups[cup_ip] = {'id': cup_ip, 'color': 'white'}
    print(cups)
    new_cup(cups[cup_ip])
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


def reset_game():
    print('Game reset')
    emit('reset', {'data': 'Game reset'})

def new_cup(data):
    print('New cup: ', data)
    socketio.emit('new_cup', {'data': data})


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

