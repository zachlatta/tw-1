from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming requests"""
    resp = twilio.twiml.Response()
    
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
    	g.say("press 1 or something")

    return str(resp)

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
	digit_pressed = request.values.get('Digits', None)
	if digit_pressed == "1":
		resp = twilio.twiml.Response()
		resp.redirect("http://b9ff5a36.ngrok.io/twl/modified.xml")

		return str(resp)
	else:
		return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)
