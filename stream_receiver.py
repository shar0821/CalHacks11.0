import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SERVER_PORT = 50007

p = pyaudio.PyAudio()

def receive_stream():
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', SERVER_PORT))
    server_socket.listen(1)

    print("Server listening for connections...")

    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    try:
        while True:
            data = conn.recv(CHUNK)
            if not data:
                break
            stream.write(data)
    except KeyboardInterrupt:
        print("Server stopped.")

    conn.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
    server_socket.close()

receive_stream()