import os
import pyaudio
import time

from boto3 import client


def pcm2wav(path):
    os.system(('ffmpeg -f s16le -ar 16000 -ac 1 -i {} -ar 44100 -ac 2 {}.wav -y').format(path, path))

start_mp3_time = time.time()
polly = client("polly", region_name="ap-northeast-2")
response = polly.synthesize_speech(
    Text="안녕하세요",
    OutputFormat="mp3",
    VoiceId="Seoyeon")
stream = response.get("AudioStream")

with open('polly_tts.mp3', 'wb') as f:
    data = stream.read()
    f.write(data)
mp3_time = time.time() - start_mp3_time
mp3_data_len = len(data)

start_pcm_time = time.time()
polly = client("polly", region_name="ap-northeast-2")
response = polly.synthesize_speech(
    Text="안녕하세요",
    SampleRate="16000",
    OutputFormat="pcm",
    VoiceId="Seoyeon")
stream = response.get("AudioStream")

with open('polly_tts.raw', 'wb') as f:
    data = stream.read()
    f.write(data)
pcm_time = time.time() - start_pcm_time
pcm_data_len = len(data)

print("return mp3 time >>", mp3_time)
print("return pcm time >>", pcm_time)

# pcm2wav('polly_tts')

# start_time = time.time()
# polly = client("polly", region_name="ap-northeast-2")
# response = polly.synthesize_speech(Text="안녕하세요",
#                                    SampleRate="16000",
#                                    OutputFormat="pcm",
#                                    VoiceId="Seoyeon")
# stream = response.get("AudioStream")
# data = stream.read()
# print(time.time() - start_time)
# print(data)
# print(len(data))
# for i in range(int(len(data)/1024) + 1):
#     print(i)

# CHUNK = 512
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# audio = pyaudio.PyAudio()
# stream2 = audio.open(format=FORMAT,
#                     channels=CHANNELS,
#                     rate=RATE,
#                     input=True,
#                     output=True,
#                     frames_per_buffer=CHUNK)
#
# while True:
#     data = stream.read()
#     stream2.write(data, CHUNK)
#     if not data:
#         break

# stream2.stop_stream()
# stream2.close()
# audio.terminate()