import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipients = None, subject = None, text_body = None, html_body = None, email_from = None):
    login = 'gremlack@gmail.com'
    password = 'emzluelfxklahnvq'

    server = smtplib.SMTP('smtp.gmail.com:587')

    server.ehlo()
    server.starttls()
    server.login(login, password)

    msg = MIMEMultipart('alternative')
    msg ['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = recipients

    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    server.set_debuglevel(1)
    server.sendmail(msg['From'],[msg['To']],msg.as_string())
    server.quit()

#send_email(recipients='lucius165@mail.ru', subject='Test Send', text_body='Hello, World!', email_from='something')