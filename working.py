from flask import Flask, request, redirect
import twilio.twiml
from twilio.rest import TwilioRestClient

app = Flask(__name__)
account_sid = "AC471b4009becda2f23c3fe90df58dd7cc"
auth_token = "dae6dc2569f846ab2b9e2404c7b1d876"
from_number = "+19092199424"
lynn_number = "+19095291698"
#FIREBASE_URL = "https://pronto-health.firebaseio.com/"
#fb = firebase.FirebaseApplication(FIREBASE_URL, None) # Create a reference to the Firebase Application

"""
    user_update = {
        "last_msg_type": "Intro",
        "nudge_type" : 
    }
    fb.patch('/user/' + sender + '/', user_update)
    user_details = fb.get('/user', sender)
 
"""

client = TwilioRestClient(account_sid, auth_token)
def send_sms(to_number, message_body):
    client.messages.create(
        to=to_number, 
        from_=from_number,
        body=message_body    
    )    

@app.route("/", methods=['GET', 'POST'])
def receieve_sms():
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None)
    forward = "Response from " + from_number + ": " + body
    send_sms(lynn_number, forward)
    return "OK"
    
"""
    resp = twilio.twiml.Response()
    resp.message("Hello, Mobile Monkey")
    return str(resp)
"""
    
if __name__ == "__main__":
    app.run(debug=True)
    