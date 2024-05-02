from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/register_device', methods=['GET'])
def register_device():
    device_id = request.args.get('device_id', None)
    if device_id is None:
        return jsonify({'error': 'device_id is missing'}), 400


@app.route('/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'Gast')
    ip = request.remote_addr
    return f"Hallo, {name} deine IP ist{ip}!"

if __name__ == '__main__':
    app.run(debug=True)

