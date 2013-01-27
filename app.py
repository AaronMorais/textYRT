import os
import keys
from flask import Flask, request
from twilio.rest import TwilioRestClient

client = TwilioRestClient(keys.sid, keys.token)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        smsSendResponse(request.Body, request.From)
    return "Main Page."

def smsSendResponse(incomingMessage, recipient):
    responseBody = "Hi! You said: " + incomingMessage
    call = client.sms.messages.create(to=recipient, from_=keys.phoneNumber, body=responseBody)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
