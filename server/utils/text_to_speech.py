from boto3 import client

class TextToSpeech:
    def __init__(self):
        self.output = 'polly_tts.raw'

    def aws_polly(self, text):
        polly = client("polly", region_name="ap-northeast-2")
        response = polly.synthesize_speech(Text=text,
                                           SampleRate="16000",
                                           OutputFormat="pcm",
                                           VoiceId="Seoyeon")
        stream = response.get("AudioStream")
        with open(self.output, 'wb') as f:
            data = stream.read()
            f.write(data)
