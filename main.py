from flask import Flask, request, jsonify
import requests
import Cup

app = Flask(__name__)

cups = []

@app.route('/', methods=['GET'])
def base():
    return "Hello World!"


@app.route('/register_device', methods=['GET'])
def register_device():
    Cup.add_cup(request.remote_addr, cups)
    print(cups)
    return jsonify({'message': 'Device registered'}), 200

@app.route('/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'Gast')
    ip = request.remote_addr
    return f"Hallo, {name} deine IP ist{ip}!"

if __name__ == '__main__':
    app.run(debug=True)

