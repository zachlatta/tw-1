from flask import Flask, request, redirect, send_from_directory
import twilio.twiml
import urllib
import os
from pydub import AudioSegment
from nocache import nocache

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
    resp.gather(numDigits=1, action="/handle-key", method="POST")

    return str(resp)

@app.route("/sounds/out/result.mp3")
@nocache
def send_result():
    return send_from_directory("sounds/out", "result.mp3")

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    digit_pressed = request.values.get('Digits', None)

    if "*" not in digit_pressed:
        resp = twilio.twiml.Response()
        resp.record(maxLength="4", action="/handle-recording/" + digit_pressed, trim="do-not-trim")
        resp.addRedirect("/")
        return str(resp)
    else:
        for dirpath, dnames, fnames in os.walk('sounds/tracks'):
            for f in fnames:
                if f != ".gitkeep":
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

    file_handle = overlayedSound.export("./sounds/out/result.mp3", format="mp3")

    resp.play("/sounds/out/result.mp3")
    resp.addRedirect("/")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
