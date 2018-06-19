# -*- coding:utf-8 -*-

import socket
import os
import time

from server.utils import speech_to_text     # Google STT
from server.utils import aibril_connector   # Aibril Conversation
from boto3 import client                    # AWS-Polly TTS
from _thread import start_new_thread
from ffmpy import FFmpeg


HOST = ''
PORT = 7100
ADDR = (HOST, PORT)
BUFF_SIZE = 1024

stt_conn = speech_to_text.SpeechToText()
aibril_conn = aibril_connector.WatsonServer()

serverSocket = socket.socket()
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(ADDR)
serverSocket.listen(5)

def client_thread(sock):
    ### receive pcm data ###
    start_pcm_recv = time.time()
    data = clientSocket.recv(BUFF_SIZE)
    if data == b'rec':
        f = open('record', 'ab')
        while True:
            data = clientSocket.recv(BUFF_SIZE)
            if data[-3:] == b'end':
                f.write(data[:-3])
                f.close()
                break
            f.write(data)
    pcm_recv_time = time.time() - start_pcm_recv

    ### pcm to wav ###
    start_pcm2wav = time.time()
    path = 'record'
    ff = FFmpeg(inputs={path: ['-f', 's16le', '-ar', '44100', '-ac', '2']},
                outputs={''.join([path, '.wav']): '-y'})
    ff.run()
    os.unlink('record')
    pcm2wav_time = time.time() - start_pcm2wav

    ### google stt ###
    start_stt = time.time()
    text = stt_conn.audio_stt('record.wav')
    stt_time = time.time() - start_stt

    #### aibril conversation ###
    start_conv = time.time()
    answer = aibril_conn.aibril_conv(text)
    conv_time = time.time() - start_conv

    #### aws-polly tts && sending pcm data ###
    data = 'tts'
    clientSocket.send(data.encode())
    start_pcm_send = time.time()

    polly = client("polly",
                   region_name="ap-northeast-2")
    response = polly.synthesize_speech(Text=answer,
                                       SampleRate="16000",
                                       OutputFormat="pcm",
                                       VoiceId="Seoyeon")
    stream = response.get("AudioStream")
    data = stream.read()
    print("pcm data length >>", len(data))
    clientSocket.sendall(data)

    data = 'end'
    clientSocket.send(data.encode())
    pcm_send_time = time.time() - start_pcm_send

    print("1. Received pcm data     >>", pcm_recv_time)
    print("2. pcm to wav            >>", pcm2wav_time)
    print("3. stt                   >>", stt_time)
    print("4. conversation          >>", conv_time)
    print("5. Sending pcm data(tts) >>", pcm_send_time)


if __name__ == '__main__':
    while True:
        clientSocket, addr = serverSocket.accept()
        print("Connected from", addr)

        start_new_thread(client_thread, (clientSocket, ))
