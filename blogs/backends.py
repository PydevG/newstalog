from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Look for a user with the provided email
            user = User.objects.get(email=email)
            # Check the password and return the user if it's correct
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
