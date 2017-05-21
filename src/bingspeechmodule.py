import requests
import httplib
import uuid
import json
from urllib import urlencode
from urllib2 import Request,urlopen,URLError,HTTPError
import wave, struct,math

class BingSpeech():
    def __init__(self, secret):
        self.sub_key = secret
        self.token = None
        pass

    def get_speech_token(self):
        FetchTokenURI = "/sts/v1.0/issueToken"
        header = {'Ocp-Apim-Subscription-Key': self.sub_key}
        conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
        body = ""
        conn.request("POST", FetchTokenURI, body, header)
        response = conn.getresponse()
        str_data = response.read()
        conn.close()
        self.token = str_data
        print "Got Token: ", self.token
        return True

    def transcribe(self,speech_file):

        # Grab the token if we need it
        if self.token is None:
            print "No Token... Getting one"
            self.get_speech_token()
		
        content_type = 'audio/wav; codec="audio/pcm"; samplerate=16000'
	
        def stream_audio_file(speech_file,chunk_size=1024):
            with open(speech_file, 'r') as f:
		while 1:
                    data = f.read(1024)
                    if not data:
			f.close()
                        break
                    yield data

	def stream_audio_file2(speech_file):
	    with open(speech_file, 'rb') as f:
		data = f.read()
		f.close()
		return data
	
	def get_raw_audio(speech_file, chunk_size=1024):
	    with open(speech_file, 'rb') as f:
		data = None
		while 1:
		    data = f.read(1024)
		    if not data:
			break
		return data

	endpoint = "https://speech.platform.bing.com/recognize/query?{0}".format(urlencode({
            "version": "3.0",
            "requestid": uuid.uuid4(),
            "appID": "D4D52672-91D7-4C74-8AD8-42B1D98141A5",
            "format": "json",
            "locale": "en-US",
            "device.os": "linux",
            "scenarios": "ulm",
            "instanceid": uuid.uuid4(),
            "result.profanitymarkup": "0"
        }))

        headers = {'Authorization': 'Bearer ' + self.token,
		   'Content-Type': content_type}

        resp = requests.post(endpoint,
                            data=stream_audio_file(speech_file),
			                stream=True,
                            headers=headers)

    val = json.loads(resp.text)
    # Return user utterance in text
    return val["results"][0]["name"]

if __name__ == "__main__":
    ms_asr = BingSpeech()
    ms_asr.get_speech_token()
    text, confidence = ms_asr.transcribe('sound.wav')
    print "Text: ", text
    print "Confidence: ", confidence
