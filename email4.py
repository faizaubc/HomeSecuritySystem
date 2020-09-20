
import smtplib
'''
s= smtplib.SMTP('smtp.gmail.com',587)
s.starttls()
s.login('capstonefaizajoseph@gmail.com', 'faizajoseph123!')

message = 'Hi there, sending this email from Python !'
s.sendmail('capstonefaizajoseph@gmail.com', 'capstonefaizajoseph@gmail.com',message)
s.quit();
'''

#https://medium.com/@sdoshi579/to-send-an-email-along-with-attachment-using-smtp-7852e77623
#Don't save this as email.py. There already exists a module names email.py, so you might run into trouble if you do
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import mimetypes
import email.mime.application

def pictureSave(path):

    sender_address = 'capstonefaizajoseph@gmail.com' #Replace with our capstone email
    password = 'faizajoseph123!' #Replace with our password
    target_address = 'capstonefaizajoseph@gmail.com' #Replace with our capstone email

    msg = MIMEMultipart()
    msg['Subject'] = 'This is the subject'
    msg['From'] = sender_address
    msg['To'] = target_address

    text = MIMEText('This is the body of the email')
    msg.attach(text)

    #The body and the attachments for the mail

    attach_file_name = path #Replace with path of image you want to send as attachment - r indicates raw string
    attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
    payload = MIMEBase('image', 'jpg') #2nd param is the file type of the image you want to send
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload) #encode the attachment

    #add payload header with filename
    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    msg.attach(payload)

    #Connect and send mail
    s = smtplib.SMTP('smtp.gmail.com',587)
    s.starttls()
    s.login(sender_address, password)
    s.send_message(msg)
    s.quit()
