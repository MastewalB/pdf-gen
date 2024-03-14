from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class AdminAuthBackend(BaseBackend):

    @staticmethod
    def authenticate(username = None, password = None):
        login_valid = settings.ADMIN_LOGIN == username
        pwd_valid = settings.ADMIN_PASSWORD == password

        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        raise ValueError("Incorrect Login Credential")
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
    @staticmethod
    def encode_token(user):
        token = RefreshToken.for_user(user)
        token.payload['TOKEN_TYPE_CLAIM'] = 'access'
        return {
            'refresh': str(token),
            'access': str(token.access_token)
        }