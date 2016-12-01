'''Receive messages through twilio API and send to gmail'''

from flask import Flask, request, redirect, make_response
from twilio import twiml
from twilio.rest import TwilioRestClient
from datetime import datetime, timedelta
# import sendgrid
# import os
# from sendgrid.helpers.mail import *
# import smtplib
# from email.mime.text import MIMEText

app = Flask(__name__)
account_sid = "AC471b4009becda2f23c3fe90df58dd7cc"
auth_token = "dae6dc2569f846ab2b9e2404c7b1d876"
from_number = "+19092199424"
lynn_number = "+19095291698"
velina_number = '+18036736204'
velina_email = 'velina.kozareva@gmail.com'
days = {'Monday':[1, ['monday', 'mon'], 'Tuesday': [2, ['tuesday', 'tues', 'tue']], 'Wednesday': [3, ['wednesday', 'wed']], 
        'Thursday': [4, ['thursday', 'thurs', 'thur']], 'Friday': [5, ['friday', 'fri']], 'Saturday': [6, ['saturday', 'sat']],
        'Sunday': [0, ['sunday', 'sun']]}    
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

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

def message_client(message_body, message_log, appt_set):
    twml = twiml.Response()
    twml.message(message_body)

    resp = make_response(str(twml))

    expires = datetime.utcnow() + timedelta(hours=4)
    resp.set_cookie('message_log', value= str(message_log), expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))
    resp.set_cookie('appt_set', value= str(appt_set), expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))
    return resp

@app.route("/", methods=['GET', 'POST'])
def receieve_sms():
    report_back = False

    from_number = request.values.get('From', None)
    body = request.values.get('Body', '')
    response = 'hello'
    previous_message = request.cookies.get('previous_message', 'None')
    message_log = request.cookies.get('message_log', '')
    appt_set = request.cookies.get('appt_set', '')
    to_number = velina_number 

    update_appt = '{} {}'.format(appt_set, '')

    if body.lower().find('between') > -1 or body.lower().find('help') > -1 or body.lower().find('options') > -1:
        update_log = '{} \n {} \n {}'.format(message_log, body, 'AWAITING RESPONSE')
        send_sms(to_number, update_log)

    update_log = '{} \n {} \n {}'.format(message_log, body, response)
    twiml_body = message_client(response, update_log, update_appt)

    wanted_days = []
    for (key, abbrev) in [(key, abbrev) for key, abbrevs in days.items() for abbrev in abbrevs[1]]:
        if body.lower().find(abbrev) > -1:
            wanted_days.append(key)


    #if 


    time = None
    wanted_time = {}
    if body.find('am') > -1 or body.find('pm') > -1:
        time_pos = body.find('am') or body.find('pm')
        if body.find(':') > -1:
            # +6 to account for space between time and 'pm'/'am'
            time = {
                'text': body[body.find(':')-1:body.find(':')+6],
                'hour': int(body[body.find(':')-1]),
                'minute': int(body[body.find(':')+1:body.find(':')+3]),
            }
        else:
            time = {
                'text': body[time_pos-1:time_pos+3],
                'hour': int(body[time_pos-1]),
                'minute': 0,
            }
        time['add'] = body[time_pos:time_pos+3]
    else:
        if body.find(':') > -1:
            time = {
                'text': body[body.find(':')-1:body.find(':')+3],
                'hour': int(body[body.find(':')-1]),
                'minute': int(body[body.find(':')+1:body.find(':')+3]),
                'add': ''
            }
    if time:
        if body.lower().find('before') > -1:
            time['hour'] = time['hour'] - 1
            #response = 'Ok, you are scheduled for {}'.format(time)
        elif body.lower().find('after') > -1:
            time['hour'] = time['hour'] + 1
        else:
            time['hour']

    if body.lower() == 'yes':
        response = 'Please text back days next week (Monday-Sunday) during which you would be able to schedule an appointment, or "more options" if next week does not work for you.'
    
    if body.lower().find('where') >-1:
        response = response + '\n We are located at 13768 Roswell Ave. in Chino off the 71'
    else:
        response = "Response from {}: {}".format(from_number, body)
        to_number = velina_number

    #send_sms(to_number, response)
    #send_email(velina_email, from_number, response)
    
    return twiml_body if twiml_body else "OK"
    
if __name__ == "__main__":
    app.run(debug=True)

 # resp = twilio.twiml.Response()
    # resp.message("Hello, Mobile Monkey")
    # return str(resp)

# attempted email code

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