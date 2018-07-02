# -*- coding: utf-8 -*-

from __future__ import division

import re
import sys
import socket

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


class Artik(object):
    def __init__(self):
        self.HOST = ''
        self.PORT = 7100
        self.BUFF = 1024
        self.ADDR = (self.HOST, self.PORT)

        self.serverSocket = socket.socket()
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(self.ADDR)
        self.serverSocket.listen(5)

    def generator(self):
        self.clientSocket, self.addr = self.serverSocket.accept()
        print('Connected from', self.addr)

        data = self.clientSocket.recv(self.BUFF)
        if data == b'rec':
            while True:
                data = self.clientSocket.recv(self.BUFF)
                if data[-3:] == b'end':
                    yield data[:-3]
                    break
                yield data
        self.clientSocket.close()


def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            print("USER >>", transcript + overwrite_chars)
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break
            num_chars_printed = 0


def main(audio_generator):
    client = speech.SpeechClient()
    config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                                     sample_rate_hertz=16000,
                                     language_code='ko-KR')
    streaming_config = types.StreamingRecognitionConfig(config=config,
                                                        interim_results=True)
    requests = (types.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator)
    responses = client.streaming_recognize(streaming_config, requests)
    listen_print_loop(responses)


if __name__ == '__main__':
    while True:
        print('')
        print('Waiting for Connection...')
        try:
            artik = Artik().generator()
            main(audio_generator=artik)
        except Exception as e:
            print('[Error]', e)
            if e[:3] == 400:
                artik = Artik().generator()
                main(audio_generator=artik)
            else:
                sys.exit()
