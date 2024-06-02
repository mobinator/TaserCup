

class SerialHandler:

    def __init__(self, serial):
        self.ser = serial

    def read_serial_data(self, func):
        # without decorator
        while True:
            data = self.ser.readline().decode().strip()
            func(data)


    def write_serial_data(self, data):
        self.ser.write(data.encode())

    def close(self):
        self.ser.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



