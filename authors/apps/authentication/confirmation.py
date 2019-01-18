"""Confirm account"""
import os

from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes

from .models import User
from .backends import account_activation_token


def send_confirmation_email(credentials, request):
    """
    This is a function that sends the EmailMessage to the user
    embedded with tokens and user id
    """
    registered_user = User.objects.get(email=credentials.get('email'))

    # send an email to the user with the token
    mail_subject = 'Activate your account.'
    current_site = os.getenv('ACCOUNT_ACTIVATION_URL')
    uid = urlsafe_base64_encode(force_bytes(registered_user.pk)).decode()
    token = account_activation_token.make_token(registered_user)
    activation_link = "{0}/{1}/{2}".format(current_site, uid, token)
    message = "Hello {0},\n {1}".format(
                            registered_user.username, activation_link)
    to_email = credentials.get('email')
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
