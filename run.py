from flask import Flask, request, redirect
import twilio.twiml
import urllib
import os
from pydub import AudioSegment

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def root():
    """Respond to incoming requests"""
    resp = twilio.twiml.Response()
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("Press 1 to beep beep")

    return str(resp)

def _overlayAllSounds(manySounds):
    #If there are no sounds there it should crash lol
    combinedsound = manySounds[0] 
    for sound in manySounds[1:]:
        combinedsound = sound.overlay(combinedsound)
    return combinedsound

def _getAudioSegmentsFromUrls(urls):
    sounds = []
    for soundUrl in manySoundUrls:
        urllib.urlretrieve(soundUrl, filename="sounds/" + str(someVal))
        somesound = AudioSegment.from_file("sounds/" + str(someVal))
        sounds.append(somesound)
        someVal += 1

def getSoundFromManySounds(manySoundUrls):
    audiosegments = _getAudioSegmentsFromUrls(manySoundUrls)
    overlayedsounds = _overlayAllSounds(audiosegments)
    return overlayedsounds

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    digit_pressed = request.values.get('Digits', None)
    print digit_pressed
    if digit_pressed == "1":
        resp = twilio.twiml.Response()
        resp.say("beep beep after the tone")
        resp.record(finishOnKey="*", maxLength="30", action="/handle-recording")
        resp.addRedirect("/")
        return str(resp)
    else:
        return redirect("/")

@app.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():

    recording_url = request.values.get("RecordingUrl", None)
    resp = twilio.twiml.Response()
    resp.say("this is your tones")
    resp.play(recording_url)
    print recording_url
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
