from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.forms import forms
from datetime import datetime

class Signup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ap_id = models.AutoField(primary_key=True)
    ap_email = models.EmailField()
    ap_mob = models.CharField(max_length=12)
    ap_ip_addr = models.GenericIPAddressField(protocol='both')
    ap_pass = models.CharField(max_length=14)  # widget=forms.PasswordInput()
    ap_date = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return str(self.user)
