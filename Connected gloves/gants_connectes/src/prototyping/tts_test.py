import gtts
from playsound import playsound
import os

Message = "Bonjour, je m'appelle Thomas !"
speech = gtts.gTTS(text = Message, lang='fr')
speech.save('SpeechFile.mp3')
#print(gtts.lang.tts_langs())
#playsound(r'/home/pi/Documents/gants_connectes/gants_connectes/code_raspberry/DataFlair.mp3')
os.system("lame --decode SpeechFile.mp3 SpeechFile.wav")
os.system("aplay SpeechFile.wav")


"""
import pyttsx3
# initialize Text-to-speech engine
engine = pyttsx3.init()
#print(engine.getProperty("lang"))
# convert this text to speech
text = "Bonjour, je m'appelle Thomas !"
print(engine.getProperty("voices"))
engine.setProperty("voice", engine.getProperty("voices")[1].id)
engine.say(text)
# play the speech
engine.runAndWait()
:"""
