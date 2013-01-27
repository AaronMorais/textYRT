import os
import keys
from flask import Flask, request
from twilio.rest import TwilioRestClient

client = TwilioRestClient(keys.sid, keys.token)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    pageString = "Hi POSTMAN!"
    if request.method == 'POST':
        clientNumber = request.args.get('From');
        clientTextContent = request.args.get('Body').lower()
        client.sms.messages.create(to=clientNumber, from_=keys.phoneNumber, body= clientTextContent)
    else:
        pageString = "Hello World!"
    return pageString

@app.route('/sendMessage/<messageBody>')
def sendMessage(messageBody):
    return "Message " + messageBody + " has been sent."

def smsSendResponse(incomingMessage):
    responseBody = incomingMessage
    call = client.sms.messages.create(to="4168460453", from_=keys.phoneNumber, body=responseBody)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
