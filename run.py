from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def root():
    """Respond to incoming requests"""
    resp = twilio.twiml.Response()
    with resp.gather(finishOnKey="*", action="/handle-key", method="POST") as g:
    	g.say("Play that trill trap shit bro")

    return str(resp)

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
	digit_pressed = request.values.get('Digits', None)
	if digit_pressed == "1":
		resp = twilio.twiml.Response() 
                resp.play("http://demo.twilio.com/hellomonkey/monkey.mp3")
		return str(resp)
	else:
		return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)
