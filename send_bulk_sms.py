# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import TwilioRestClient
import pyexcel as pe
    

# Find these values at https://twilio.com/user/account
account_sid = "AC471b4009becda2f23c3fe90df58dd7cc"
auth_token = "dae6dc2569f846ab2b9e2404c7b1d876"
from_number = "+19092199424"
input_file_name = "pronto_health_v1.csv"

client = TwilioRestClient(account_sid, auth_token)

def send_sms(to_number, message_body):
    client.messages.create(
        to=to_number, 
        from_=from_number,
        body=message_body    
    )  
    
records = pe.get_records(file_name=input_file_name)
for record in records:
        send_sms(record['Phone_Number'],record['Message'])
        print "Sent message to: ", record['Phone_Number']