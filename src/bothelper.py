import soundfile as sf
import clipaudiomodule as ca
import bingspeechmodule as bs
import bingttsmodule as bt
import luismodule as luis

class BotHelper():

    def convert_audio(self):
		myfile = sf.SoundFile('input.wav',mode='r',format='RAW',samplerate=16000,channels=1,subtype='PCM_16')
		sf.write('converted.wav',myfile.read(),16000,subtype='PCM_16',format='WAV')

    def trim_audio(self):
		trimmer = ca.AudioTrimmer()
		# Saves trimmed audio to trimmed.wav
		trimmer.trim_audio('converted.wav') 

    def recognize_speech(self):
		spr = bs.BingSpeech('YOUR_BING_SPEECH_KEY')
		# Take from trimmed data
		res = spr.transcribe('trimmed.wav')
		print res
		return res

    def get_response(self):
		# speech to text
		translator = bt.Translator('YOUR_BING_SPEECH_KEY')
		text = self.recognize_speech()
		# get bot response
		reply = luis.get_luis_response(text)
		print reply
		# text to speech
		output = translator.speak(reply, "en-US", "Female", "riff-16khz-16bit-mono-pcm")
		with open("botresponse.wav", "w") as f:
				f.write(output)

    def generate_response(self):
		self.convert_audio()
		self.trim_audio()
		self.get_response()
