from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64


def create_message(sender: str, to: str, subject: str, body: str, subtype: str):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(body, subtype))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw_message
