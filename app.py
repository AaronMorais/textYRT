import os
import keys
from flask import Flask, request, redirect, session
from twilio.rest import TwilioRestClient
import twilio.twiml

client = TwilioRestClient(keys.sid, keys.token)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    body = "Hello "
    if(request.args.get('Body')):
        body += request.args.get('Body')
    resp = twilio.twiml.Response()
    resp.sms(body)
    return str(resp)

@app.route('/sendMessage/<messageBody>')
def sendMessage(messageBody):
    smsSendResponse(messageBody)
    return "Message " + messageBody + " has been sent."

def smsSendResponse(incomingMessage):
    responseBody = incomingMessage
    call = client.sms.messages.create(to="4168460453", from_=keys.phoneNumber, body=responseBody)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
