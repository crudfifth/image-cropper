from .constants import SENDER_EMAIL, REPLY_TO_EMAIL
from django.core.mail import EmailMessage

def send_mail_from_service(subject, body, to):
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=SENDER_EMAIL,
        to=to,
        reply_to=[REPLY_TO_EMAIL]
    )
    email.send()