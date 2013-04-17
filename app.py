import os
import keys
from flask import Flask, request
from twilio.rest import TwilioRestClient
import twilio.twiml
from tf import *

schedule = None
client = TwilioRestClient(keys.sid, keys.token)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return "Text-YRT can send you the latest stop times for your YRT bus stop!"

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    global schedule
    if schedule is None:
        schedule = createScheduleInstance()
        
    #parse body parameter from request
    requestBody = str(request.args.get('Body')) 

    #immediately fail if request is not a 4 digit number
    if len(requestBody) != 4 or requestBody.isdigit() != True:
        return "Stop invalid. Please request stop times for a valid stop."

    #get next bus times from tf.py
    nextBusTimes = getNextBusTimes(schedule, requestBody, 5)
    if nextBusTimes is None:
        return "Sorry! The stop you requested does not exist or an error occured." 

    #send response to twilio
    responseString = requestBody 
    responseString += "\n" + nextBusTimes
    twilioResponse = twilio.twiml.Response()
    twilioResponse.sms(responseString)
    return str(twilioResponse)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) #get environment defined port for deployment
    app.run(host='0.0.0.0', port=port)