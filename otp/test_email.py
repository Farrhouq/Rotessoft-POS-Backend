import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_otp_email(otp, email):
    message = Mail(
        from_email='no-reply@farouqimoro@gmail.com',
        to_emails=email,
        subject='Sending with Twilio SendGrid is Fun',
        plain_text_content='<strong>and easy to do anywhere, even with Python</strong>'
    )
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
    except Exception as e:
        print(e)
