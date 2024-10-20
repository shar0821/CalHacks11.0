import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SERVER_IP = '127.0.0.1'
SERVER_PORT = 50007

p = pyaudio.PyAudio()

def send_stream():
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    print("Streaming audio to the server...")

    try:
        while True:
            data = stream.read(CHUNK)
            client_socket.sendall(data)
    except KeyboardInterrupt:
        print("Streaming stopped.")

    stream.stop_stream()
    stream.close()
    p.terminate()
    client_socket.close()

send_stream()