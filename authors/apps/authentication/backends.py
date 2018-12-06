import datetime
import logging

import jwt

# from django.conf import settings
#
# from rest_framework import authentication, exceptions
#
# from .models import User
from django.conf import settings

"""Configure JWT Here"""
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

# Get an instance of a logger
logger = logging.getLogger(__name__)


class JWTAuthentication(JSONWebTokenAuthentication):
    """Inherit the JSON web authentication class from rest_framework_jwt"""

    @staticmethod
    def generate_token(user, is_refresh_token=False):
        """
        generate a payload token
        :param user:
        :param is_refresh_token:
        :return:
        """
        secret = settings.SECRET_KEY
        token = jwt.encode({
            'username': user.username,
            'refresh_token': is_refresh_token,
            'iat': datetime.datetime.utcnow(),
            'nbf': datetime.datetime.utcnow() + datetime.timedelta(minutes=-5),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, secret)
        token = str(token)
        logger.debug("is_refresh_token : %s : %s" % (is_refresh_token, token))
        return token

    @staticmethod
    def generate_reset_token(email):
        """ generates reset password token """

        token = jwt.encode(
            {
                "email": email,
                "iat": datetime.datetime.utcnow(),
                "exp": datetime.datetime.utcnow() +
                datetime.timedelta(
                    minutes=720)},
            settings.SECRET_KEY,
            algorithm='HS256').decode()
        return token
