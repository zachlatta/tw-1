from flask import Flask, request, redirect, send_from_directory
import twilio.twiml
import urllib
import os
from pydub import AudioSegment
import uuid

app = Flask(__name__)

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

@app.route("/", methods=['GET', 'POST'])
def root():
    """Respond to initial call"""
    resp = twilio.twiml.Response()

    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("Press anything to beep beep")

    return str(resp)

@app.route("/sounds/out/<f>")
def send_result(f):
    return send_from_directory("sounds/out", f)

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    digit_pressed = request.values.get('Digits', None)

    if "*" not in digit_pressed:
        resp = twilio.twiml.Response()
        resp.record(maxLength="4", action="/handle-recording/" + digit_pressed)
        resp.addRedirect("/")
        return str(resp)
    else:
        for dirpath, dnames, fnames in os.walk('sounds/tracks'):
            for f in fnames:
                os.remove(os.path.join(dirpath, f))

        resp = twilio.twiml.Response()
        resp.addRedirect("/")
        return str(resp)


@app.route("/handle-recording/<int:number>", methods=['GET', 'POST'])
def handle_recording(number):
    recording_url = request.values.get("RecordingUrl", None)
    urllib.urlretrieve(recording_url, filename="sounds/tracks/" +  str(number) + ".wav")
    resp = twilio.twiml.Response()
    callid = request.form.get('CallSid')
    someSounds = []
    for dirpath, dnames, fnames in os.walk('sounds/tracks'):
        for f in fnames:
            if f != ".gitkeep":
                someSounds.append(AudioSegment.from_wav(os.path.join(dirpath, f)))
    overlayedSound = _overlayAllSounds(someSounds)

    filename = str(uuid.uuid4()) + ".mp3"
    file_handle = overlayedSound.export("./sounds/out/" + filename, format="mp3")

    resp.play("/sounds/out/" + filename)
    resp.addRedirect("/")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
