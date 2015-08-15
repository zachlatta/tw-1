from flask import Flask, request, redirect
import twilio.twiml
from tables import *
import db

app = Flask(__name__)
db = db.DB()

@app.route("/", methods=['GET', 'POST'])
def root():
    """Respond to incoming requests"""
    resp = twilio.twiml.Response()
    print request.form.get('CallSid')
    callid = db.addEntry(Calls(request.form.get('CallSid'), request.form.get('From'), str(list())))
    print callid
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("Press 1 to beep beep")

    return str(resp)

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        resp = twilio.twiml.Response()
        # resp.play("http://demo.twilio.com/hellomonkey/monkey.mp3")
        resp.say("beep")
        resp.record(finishOnKey="*", maxLength="30", action="/handle-recording")
        resp.addRedirect("/")
        return str(resp)
    else:
        return redirect("/")

@app.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():

    recording_url = request.values.get("RecordingUrl", None)
    resp = twilio.twiml.Response()
    callid = request.form.get('CallSid')
    print callid
    db.updateEntry(Calls, callid, {'recordings': recording_url})
    resp.say("this is your tones")
    resp.play(recording_url)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
