import os
import socket
import pyaudio


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 10)
RECORD_SEC = 60

HOST = '192.168.0.5'
PORT = 7103
ADDR = (HOST, PORT)
BUFF_SIZE = 1024

### send pcm data ###
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientSocket.connect(ADDR)

data = 'rec'
clientSocket.send(data.encode())

for i in range(0, int(RATE / CHUNK * RECORD_SEC)):
  try:
    clientSocket.sendall(stream.read(CHUNK))
  except Exception as e:
    print(e)

data = 'end'
clientSocket.send(data.encode())

stream.stop_stream()
stream.close()
audio.terminate()
