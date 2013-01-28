import os
import keys
from flask import Flask, request, redirect, session
from twilio.rest import TwilioRestClient
import twilio.twiml

client = TwilioRestClient(keys.sid, keys.token)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    requestBody = str(request.args.get('Body'))
    body = requestBody + " Results: Coming Soon!"
    if len(requestBody) != 4 or requestBody.isdigit != True:
        body = "Stop " + requestBody + " does not exist."
    resp = twilio.twiml.Response()
    resp.sms(body)
    return str(resp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
