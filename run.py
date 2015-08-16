from flask import Flask, request, redirect, send_from_directory
from pydub import AudioSegment
from twilio.rest import TwilioRestClient
import os, errno
import twilio.twiml
import urllib
import uuid
import soundcloud


SOUND_CLOUD_CLIENT_ID = os.environ.get("SC_CID")
SOUND_CLOUD_CLIENT_SECRET = os.environ.get("SC_SECRET")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

SOFT_GAIN=-15.0
NORMAL_GAIN=-7.0
LOUD_GAIN=-2.0

GAIN_MAPPING = {
    1: SOFT_GAIN,
    2: SOFT_GAIN,
    3: SOFT_GAIN,
    4: NORMAL_GAIN,
    5: NORMAL_GAIN,
    6: NORMAL_GAIN,
    7: LOUD_GAIN,
    8: LOUD_GAIN,
    9: LOUD_GAIN
}

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

def adjust_gain(filename, format, gain):
    sound = AudioSegment.from_file(filename, format=format)
    adjusted_sound = sound + gain
    adjusted_sound.export(filename, format=format)

@app.route("/", methods=['GET', 'POST'])
def root():
    """Respond to initial call"""
    resp = twilio.twiml.Response()
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        # g.play('/sounds/out/' + os.readlink('sounds/out/most_recent.mp3'))
        g.say("Press a number to record a track or press * to clear")

    return str(resp)

@app.route("/loop", methods=['GET', 'POST'])
def looper():
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
    fromNumber = request.form.get("From")
    toNumber = request.form.get("To")

    if "*" not in digit_pressed:
        resp = twilio.twiml.Response()
        resp.record(maxLength="6", action="/handle-recording/" + digit_pressed + "/" + str(fromNumber) + "/" + str(toNumber), trim="do-not-trim")
        resp.addRedirect("/loop")
        return str(resp)
    else:
        for dirpath, dnames, fnames in os.walk('sounds/tracks'):
            for f in fnames:
                if f != ".gitkeep":
                    os.remove(os.path.join(dirpath, f))

        set_most_recent_result("blank.mp3")
        resp = twilio.twiml.Response()
        resp.addRedirect("/loop")
        return str(resp)

@app.route('/redirectSoundcloud')
def soundcloud_redirect():
    code = requests.values.get("code")
    access_token = client.exchange_token(code)

@app.route("/handle-recording/<int:number>/<fromNumber>/<toNumber>", methods=['GET', 'POST'])
def handle_recording(number,fromNumber, toNumber):
    recording_url = request.values.get("RecordingUrl", None)
    filename = "sounds/tracks/" + str(number) + ".wav"
    urllib.urlretrieve(recording_url, filename=filename)

    adjust_gain(filename, "wav", GAIN_MAPPING.get(number, 0.0))

    resp = twilio.twiml.Response()
    resp.say("beep")
    callid = request.form.get('CallSid')
    someSounds = []
    for dirpath, dnames, fnames in os.walk('sounds/tracks'):
        for f in fnames:
            if f != ".gitkeep":
                someSounds.append(AudioSegment.from_wav(os.path.join(dirpath, f)))
    overlayedSound = _overlayAllSounds(someSounds)
    filename = str(uuid.uuid4()) + ".mp3"
    file_handle = overlayedSound.export("./sounds/out/" + filename, format="mp3")
    client = soundcloud.Client(username = "t9soundcloud@christran.in",password = os.environ.get("SC_PASS"), client_id = SOUND_CLOUD_CLIENT_ID, client_secret = SOUND_CLOUD_CLIENT_SECRET)
    print client

    track = client.post('/tracks', track = {
        'title': heroku(),
        'asset_data': open('./sounds/out/' + filename, 'rb')
    })

    tracks = map(lambda id: dict(id=id), [track.id])

    playlist = client.get('/me/playlists')[0]

    client.put(playlist.uri, playlist={
        'tracks': tracks
    })

    twilioClient = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    sms = twilioClient.sms.messages.create(body =
                                          "Your sick jam just got uploaded on SoundCloud! Check it out here: " + track.permalink_url, to=fromNumber, from_=toNumber)
    print "Yoyoyo! Sick tune got uploaded at: " + track.permalink_url
    set_most_recent_result(filename)
    resp.play("/sounds/out/" + filename)
    resp.addRedirect("/loop")
    return str(resp)

from random import choice
def heroku(hex=False):
    # modified by @dentearl https://gist.github.com/3442096
    # who forked from @hasenj https://gist.github.com/3205543
    # who forked from: @afriggeri https://gist.github.com/1266756
    # example output:
    # 'golden-horizon-2076'
    adjs = ['afternoon', 'aged', 'ancient', 'autumn', 'billowing',
    'bitter', 'black', 'blue', 'bold', 'broken',
    'calm', 'caring', 'cold', 'cool', 'crimson',
    'damp', 'dark', 'dawn', 'delicate', 'divine',
    'dry', 'empty', 'ephemeral', 'evening', 'falling',
    'fathomless', 'floral', 'fragrant', 'frosty', 'golden',
    'green', 'hidden', 'holy', 'icy', 'imperfect',
    'impermanent', 'late', 'lingering', 'little', 'lively',
    'long', 'majestic', 'mindful', 'misty', 'morning',
    'muddy', 'nameless', 'noble', 'old', 'patient',
    'polished', 'proud', 'purple', 'quiet', 'red',
    'restless', 'rough', 'shy', 'silent', 'silvery',
    'slender', 'small', 'smooth', 'snowy', 'solitary',
    'sparkling', 'spring', 'stately', 'still', 'strong',
    'summer', 'timeless', 'twilight', 'unknowable', 'unmovable',
    'upright', 'wandering', 'weathered', 'white', 'wild',
    'winter', 'wispy', 'withered', 'young',
    ]
    nouns = ['bird', 'breeze', 'brook', 'brook', 'bush',
    'butterfly', 'chamber', 'chasm', 'cherry', 'cliff',
    'cloud', 'darkness', 'dawn', 'dew', 'dream',
    'dust', 'eye', 'feather', 'field', 'fire',
    'firefly', 'flower', 'foam', 'fog', 'forest',
    'frog', 'frost', 'glade', 'glitter', 'grass',
    'hand', 'haze', 'hill', 'horizon', 'lake',
    'leaf', 'lily', 'meadow', 'mist', 'moon',
    'morning', 'mountain', 'night', 'paper', 'pebble',
    'pine', 'planet', 'plateau', 'pond', 'rain',
    'resonance', 'ridge', 'ring', 'river', 'sea',
    'shadow', 'shape', 'silence', 'sky', 'smoke',
    'snow', 'snowflake', 'sound', 'star', 'stream',
    'sun', 'sun', 'sunset', 'surf', 'thunder',
    'tome', 'tree', 'violet', 'voice', 'water',
    'waterfall', 'wave', 'wave', 'wildflower', 'wind',
    'wood',
    ]
    if hex:
        suffix = '0123456789abcdef'
    else:
        suffix = '0123456789'
        return ('-'.join([choice(adjs), choice(nouns), ''.join(choice(suffix) for x in xrange(4))]))




if __name__ == "__main__":
    app.run(debug=True)
