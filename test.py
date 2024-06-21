import asyncio
import serial
import websockets


# Serial communication coroutine
async def read_serial(port, baudrate, queue):
    try:
        ser = serial.Serial(port, baudrate, timeout=0)
        print(f"Listening on {port} at {baudrate} baud rate.")

        while True:
            data = ser.read(ser.in_waiting or 1)
            if data:
                line = data.decode('utf-8', errors='ignore').rstrip()
                if line:
                    print(f"Received from serial: {line}")
                    await queue.put(line)
            await asyncio.sleep(0.01)  # Yield control to the event loop

    except serial.SerialException as e:
        print(f"Serial exception: {e}")
    except asyncio.CancelledError:
        pass
    finally:
        if ser.is_open:
            ser.close()
            print("Serial port closed.")


# Websocket communication coroutine
async def websocket_handler(websocket, path, queue):
    print(f"Websocket connection from {websocket.remote_address}")
    try:
        while True:
            # Check if there is data from the serial coroutine
            if not queue.empty():
                line = await queue.get()
                await websocket.send(line)

            # Check if there is data from the websocket
            try:
                data = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                print(f"Received from socket: {data}")
                # Here you can add code to send data back to the serial if needed
            except asyncio.TimeoutError:
                pass  # No data received within the timeout period
    except asyncio.CancelledError:
        print("Websocket handler cancelled.")
    finally:
        print("Websocket connection closed.")


# Main function
async def main():
    port = "COM9"
    baudrate = 115200
    host = '0.0.0.0'
    ws_port = 8080

    # Queue for communication between coroutines
    queue = asyncio.Queue()

    # Start the serial reader coroutine
    serial_task = asyncio.create_task(read_serial(port, baudrate, queue))

    # Start the websocket server
    async with websockets.serve(lambda ws, path: websocket_handler(ws, path, queue), host, ws_port):
        print(f"Websocket server listening on {host}:{ws_port}")
        await asyncio.Future()  # Run forever


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Exiting main program.")
