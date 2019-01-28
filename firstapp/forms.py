from django import forms
from  django.contrib.auth.models import User
from  django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    MobileNo = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'MobileNo', 'password1', 'password2']
