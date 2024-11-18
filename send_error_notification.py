# scripts/send_error_notification.py
import smtplib
from email.message import EmailMessage
import os

def send_error_notification():
    msg = EmailMessage()
    msg.set_content("GitHub Actions workflow failed. Please check the logs.")
    msg['Subject'] = 'Workflow Failure Alert'
    msg['From'] = os.getenv('EMAIL_USERNAME')
    msg['To'] = os.getenv('EMAIL_USERNAME')  # Send to yourself

    server = smtplib.SMTP(os.getenv('EMAIL_HOST'), int(os.getenv('EMAIL_PORT')))
    server.starttls()
    server.login(os.getenv('EMAIL_USERNAME'), os.getenv('EMAIL_PASSWORD'))
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    send_error_notification()
