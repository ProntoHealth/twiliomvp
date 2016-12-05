'''Receive messages through twilio API and send to gmail'''

from flask import Flask, request, redirect, make_response
from twilio import twiml
from twilio.rest import TwilioRestClient
from datetime import datetime, timedelta, date
# import sendgrid
# import os
# from sendgrid.helpers.mail import *
# import smtplib
# from email.mime.text import MIMEText

app = Flask(__name__)
account_sid = "AC471b4009becda2f23c3fe90df58dd7cc"
auth_token = "dae6dc2569f846ab2b9e2404c7b1d876"
log_from_number = "+19092199424"
lynn_number = "+19095291698"
velina_number = '+18036736204'
velina_email = 'velina.kozareva@gmail.com'
days = {'Monday':[0, ['monday', 'mon']], 'Tuesday': [1, ['tuesday', 'tues', 'tue']], 'Wednesday': [2, ['wednesday', 'wed']], 
        'Thursday': [3, ['thursday', 'thurs', 'thur']], 'Friday': [4, ['friday', 'fri']], 'Saturday': [5, ['saturday', 'sat']],
        'Sunday': [6, ['sunday', 'sun']]}    
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
requirements = ['day', 'date', 'month', 'time']

today = date.today()
next_week = today.isocalendar()[1] + 1
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
def send_sms(to_number, message_body, responder):
    client.messages.create(
        to=to_number, 
        from_=log_from_number,
        body='{} From: {}'.format(message_body, responder)    
    ) 

def message_client(message_body, message_log, appt):
    twml = twiml.Response()
    twml.message(message_body)

    resp = make_response(str(twml))

    expires = datetime.utcnow() + timedelta(hours=12)
    resp.set_cookie('message_log', value= str(message_log), expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))
    for requirement in requirements:
        resp.set_cookie('appt_{}'.format(requirement), value=str(appt[requirement]), expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))

    #resp.set_cookie('appt_date', value= str(appt), expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))
    return resp

def get_time(body):
    time = None
    if body.find('am') > -1 or body.find('pm') > -1:
        time_pos = body.find('am') if body.find('am') > -1 else body.find('pm')
        if body.find(':') > -1:
            # +6 to account for space between time and 'pm'/'am'
            time = {
                'text': body[body.find(':')-1:body.find(':')+6],
                'hour': int(body[body.find(':')-1]),
                'minute': int(body[body.find(':')+1:body.find(':')+3]),
            }
        else:
            if body[time_pos-1].isdigit():
                time = {
                    'text': body[time_pos-1:time_pos+3],
                    'hour': int(body[time_pos-1]),
                    'minute': '00',
                }
            else:
                return {'hold': 'empty'}
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
        if body.find('before') > -1:
            time['hour'] = time['hour'] - 1
            #response = 'Ok, you are scheduled for {}'.format(time)
        elif body.find('after') > -1:
            time['hour'] = time['hour'] + 1
    return time

def get_date(body):
    wanted_days = []
    fulldate=None
    weekday=None
    for (key, abbrev) in [(key, abbrev) for key, value in days.items() for abbrev in value[1]]:
        if body.find(abbrev) > -1:
            wanted_days.append(key)

    if wanted_days:
        weekday = wanted_days[0]
        weekday_num = (days[weekday][0]+1)%7
        fulldate = datetime.strptime('2016-{}-{}'.format(next_week,weekday_num), '%Y-%W-%w')
        
    # specifically for december
    if body.find('12/') > -1:
        date_text = body[body.find('12/'):body.find('12/')+6]
        date_text2 = date_text.split(' ')[0]
        fulldate = datetime.strptime('{}/2016'.format(date_text2), '%m/%d/%Y')
        weekday = fulldate.strftime("%A")
        monthdate = fulldate.day
        month = fulldate.month

    return fulldate, weekday

@app.route("/", methods=['GET', 'POST'])
def receieve_sms():
    appt = {}
    
    from_number = request.values.get('From', None)
    body = request.values.get('Body', '').lower()
    response = ''
    #previous_message = request.cookies.get('previous_message', 'None')
    message_log = request.cookies.get('message_log', '')
    
    for requirement in requirements:
        appt[requirement] = request.cookies.get('appt_{}'.format(requirement), '-1')
   
    to_number = lynn_number 

    #update_appt = '{} {}'.format(appt_set, '')

    if body.find('between') > -1 or body.find('help') > -1 or body.find('options') > -1 or body.find('dec') > -1 or body.find('insurance') > -1 or body.find('unsubscribe') > -1:
        update_log = '{} --{} --{}'.format(message_log, body, 'AWAITING RESPONSE')
        send_sms(to_number, update_log, from_number)
        return 'OK'

    if body.find('where') >-1:
        response = response + '\n We are located at 13768 Roswell Ave. #118 in Chino off the 71.'
        
        update_log = '{} --{} --{}'.format(message_log, body, response)
        twiml_body = message_client(response, update_log, appt)
    
        return twiml_body

    all_info_here = True if str(appt['time']) != '-1' and str(appt['day']) != '-1' else False

    if str(appt['time']) == '-1':
        wanted_time = get_time(body)
        if wanted_time:
            if wanted_time.get('hour') in range(8,12) and wanted_time['add'] != 'pm':
                appt['time'] = '{}:{} {}'.format(wanted_time['hour'], wanted_time['minute'], wanted_time['add'])
            else:
                update_log = '{} --{} --{}'.format(message_log, body, 'AWAITING RESPONSE')
                send_sms(to_number, update_log, from_number)
                return 'OK' 

    if str(appt['day']) == '-1':
        fulldate, weekday = get_date(body)

        if fulldate:
            monthdate = fulldate.day
            month = fulldate.month
            appt['day'] = weekday
            appt['date'] = monthdate
            appt['month'] = month

    if body.find('yes') > -1 and not all_info_here:
        response = response + "Please text back days next week (Monday-Sunday) when you're free for an appointment, or 'more options' if next week does not work for you."
        
        update_log = '{} --{} --{}'.format(message_log, body, response)
        twiml_body = message_client(response, update_log, appt)
    
        return twiml_body

    if body.find('confirmed') > -1:
        response = response + 'Great, you are confirmed for {} {}/{} at {}. We will be in touch.'.format(appt['day'], appt['month'], appt['date'], appt['time'])
    elif str(appt['day']) != '-1' and str(appt['time']) == '-1':
        response = response + 'What time on {} {}/{} would work well for you? Please note we recommend a morning appointment because you will need to fast for 8 hours in advance. The clinic is open 8 am to 5 pm.'.format(appt['day'], appt['month'], appt['date'])
    elif str(appt['day']) != '-1' and str(appt['time']) != '-1':
        if all_info_here:
            update_log = '{} --{} --{}'.format(message_log, body, 'AWAITING RESPONSE')
            send_sms(to_number, update_log, from_number)
            return 'OK'
        else:
            response = response + 'Ok, we can get you in on {} {}/{} at {}. Please text "confirmed" to set this appointment.'.format(appt['day'], appt['month'], appt['date'], appt['time'])
    else:
        update_log = '{} --{} --{}'.format(message_log, body, 'AWAITING RESPONSE')
        send_sms(to_number, update_log, from_number)
        return 'OK'
    # else:
    #     response = "Response from {}: {}".format(from_number, body)
    #     to_number = velina_number

    #send_sms(to_number, response)
    #send_email(velina_email, from_number, response)
    update_log = '{} --{} --{}'.format(message_log, body, response)
    twiml_body = message_client(response, update_log, appt)
    
    return twiml_body 
    
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