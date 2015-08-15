from flask import Flask, request, redirect, send_from_directory
from pydub import AudioSegment
import os, errno
import twilio.twiml
import urllib
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

def force_symlink(file1, file2):
    try:
        os.symlink(file1, file2)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(file2)
            os.symlink(file1, file2)

def set_most_recent_result(filename):
    force_symlink(filename, "sounds/out/most_recent.mp3")

@app.route("/", methods=['GET', 'POST'])
def root():
    """Respond to initial call"""
    resp = twilio.twiml.Response()
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.play('/sounds/out/' + os.readlink('sounds/out/most_recent.mp3'))

    return str(resp)

@app.route("/sounds/out/<f>")
def send_result(f):
    return send_from_directory("sounds/out", f)

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

        set_most_recent_result("blank.mp3")
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
    set_most_recent_result(filename)

    resp.play("/sounds/out/" + filename)
    resp.addRedirect("/")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
