import os
import socket
import pyaudio
import time


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SEC = 3

HOST = ''
PORT = 7100
ADDR = (HOST, PORT)
BUFF_SIZE = 1024

### recording, send pcm data ###
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

start_rec = time.time()
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
rec_time = time.time() - start_rec

### receive pcm streaming ###
data = clientSocket.recv(BUFF_SIZE)
start_pcm_recv = time.time()
if data == b'tts':
    a = 0
    while True:
        data = clientSocket.recv(BUFF_SIZE)
        a += len(data)
        # print(data)
        FORMAT2 = pyaudio.paInt16
        CHUNK2 = 512
        CHANNELS2 = 1
        RATE2 = 8000
        audio2 = pyaudio.PyAudio()
        stream2 = audio2.open(format=FORMAT2,
                            channels=CHANNELS2,
                            rate=RATE2,
                            input=True,
                            output=True,
                            frames_per_buffer=CHUNK2)
        stream2.write(data, CHUNK2)
        if data[-3:] == b'end':
            stream2.write(data[-3:], CHUNK2)
            stream2.stop_stream()
            stream2.close()
            break
    print("pcm data length >>", a-len(data[-3:]))
pcm_recv_time = time.time() - start_pcm_recv

full_time = time.time() - start_rec

print("1. Recording time >>", rec_time)
print("2. Waiting        >>", full_time-(rec_time+pcm_recv_time))
print("3. pcm streaming  >>", pcm_recv_time)

clientSocket.close()
