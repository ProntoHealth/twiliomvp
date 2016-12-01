'''Receive messages through twilio API and send to gmail'''

from flask import Flask, request, redirect
import twilio.twiml
from twilio.rest import TwilioRestClient
# import sendgrid
# import os
#from sendgrid.helpers.mail import *
# import smtplib
# from email.mime.text import MIMEText

app = Flask(__name__)
account_sid = "AC471b4009becda2f23c3fe90df58dd7cc"
auth_token = "dae6dc2569f846ab2b9e2404c7b1d876"
from_number = "+19092199424"
lynn_number = "+19095291698"
velina_number = '+18036736204'
velina_email = 'velina.kozareva@gmail.com'

#numbers = []
#FIREBASE_URL = "https://pronto-health.firebaseio.com/"
#fb = firebase.FirebaseApplication(FIREBASE_URL, None) # Create a reference to the Firebase Application

# """
#     user_update = {
#         "last_msg_type": "Intro",
#         "nudge_type" : 
#     }
#     fb.patch('/user/' + sender + '/', user_update)
#     user_details = fb.get('/user', sender)
 
# """
# @app.route("/")
# def index():
#   return "Hello World"


client = TwilioRestClient(account_sid, auth_token)
def send_sms(to_number, message_body):
    client.messages.create(
        to=to_number, 
        from=from_number,
        body=message_body    
    ) 

# def send_email(to_email, from_number, message_body):
#     sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
#     from_email = velina_email
#     subject = "Hello World from the SendGrid Python Library!"
#     content = Content("text/plain", "Hello, Email!")
#     mail = Mail(from_email, subject, to_email, content)
#     response = sg.client.mail.send.post(request_body=mail.get())
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)   

# def send_email(to_email, from_number, message_body):
#     msg = MIMEText(message_body, 'plain')
#     msg['Subject'] = 'New message from {}'.format(from_number)
#     msg['From'] = from_email
#     msg['To'] = to_email

#     s = smtplib.SMTP('localhost')
#     s.sendmail(from_email, to_email, msg.as_string())
#     s.quit()

@app.route("/", methods=['GET', 'POST'])
def receieve_sms():
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None)
    forward = "Response from {}: {}".format(from_number, body)
    to_number = from_number 

    if body.lower() == 'yes':
        forward = 'Please text back days next week (Monday-Friday) during which you would be able to schedule an appointment, "where" if you would like to know where the clinic is located, or "more info" if you have questions about insurance or other details.'
    elif 'where' in body.lower().split(' '):
        forward = 'We are located at 13768 Roswell Ave. in Chino off the 71. Please text back days (Monday-Friday) during which you would be able to schedule an appointment, or "more info" if you have further questions.'
    else:
        forward = "Response from {}: {}".format(from_number, body)
        to_number = velina_number

    send_sms(to_number, forward)
    #send_email(velina_email, from_number, forward)
    return "OK"

    # resp = twilio.twiml.Response()
    # resp.message("Hello, Mobile Monkey")
    # return str(resp)

    
if __name__ == "__main__":
    app.run(debug=True)
    