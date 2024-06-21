from flask_socketio import SocketIO
from flask_serial import Serial

cup_colors = ['white', 'red', 'green']
cup_states = ['steht', 'wird aufgehoben', 'trinken', 'wird abgestellt']
game_states = ['waiting', 'countdown', 'running']


class Cup:

    def __init__(self, cup_id: str, color: str, name: str, brightness: int, socket_io: SocketIO, serial: Serial):
        self.id = cup_id
        self.color = color
        self.name = name
        self.state = cup_states[0]
        self.socketIO = socket_io
        self.serial = serial
        self.safe = True

        self.standing_brightness = brightness
        self.last_z_acceleration = 0

    def update(self, brightness: int, z_acceleration: float, game_state: str):
        self.update_cup_state(brightness, z_acceleration)
        self.last_z_acceleration = z_acceleration

        if game_state == "countdown" and self.state == cup_states[1] and not self.safe:
            print("Cup picked up to early!")
            self.activate_taser()

    def to_json(self):
        return {
            'id': self.id,
            'color': self.color,
            'name': self.name
        }

    def set_cup_color(self, new_color: str):
        self.color = new_color

        self.socketIO.emit('cup_state', {'data': self.to_json()})

    def update_cup_state(self, brightness: int, z_acceleration: float):

        if self.state == cup_states[0]:
            if brightness > self.standing_brightness + 40 and z_acceleration > 5.5 and self.last_z_acceleration > 5.5:
                self.state = cup_states[1]
                print(f'Cup {self.id} picked up')

        elif self.state == cup_states[1]:
            if z_acceleration < 1 and self.last_z_acceleration < 1:
                self.state = cup_states[2]
                print(f'Cup {self.id} drinking')

        elif self.state == cup_states[2]:
            if z_acceleration > 5.5:
                self.state = cup_states[3]
                print(f'Cup {self.id} put down')

        elif self.state == cup_states[3]:
            if 5.1 > z_acceleration > 4.9 and 5.1 > self.last_z_acceleration > 4.9 and brightness < self.standing_brightness + 40:
                self.state = cup_states[0]
                print(f'Cup {self.id} is standing again')

            if z_acceleration < 1 and self.last_z_acceleration < 1:
                self.state = cup_states[2]
                print(f'Cup {self.id} drinking')

    def activate_taser(self):
        if not self.safe:
            print('Taser activated')
            self.serial.on_send(f'TASE {self.id} 100 \r\n')
            self.update_color('red')
        else:
            print(f'Taser not activated Cup: {self.id} is safe')

        self.safe = True

    def put_down_cup(self):
        self.safe = True
        self.update_color('green')

    def update_color(self, color: str):
        self.color = color
        self.socketIO.emit('cup_state', {'data': self.to_json()})

    def __str__(self):
        return f'Cup {self.id}: {self.color}, name: {self.name}, state: {self.state}'
