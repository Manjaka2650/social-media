
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm


class UserCreation(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'username', 'email', 'password1', 'password2'] 
        