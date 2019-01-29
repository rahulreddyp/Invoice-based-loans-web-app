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

class Business(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank= True)
    b_id = models.AutoField(primary_key=True)
    b_name = models.CharField(max_length=30)
    b_owner_name = models.CharField(max_length=30)
    b_contact = models.CharField(max_length=12)
    b_addr = models.TextField()
    b_pan_no = models.CharField(max_length=10)
    b_est_date = models.DateField()
    b_type = models.CharField(max_length=20)
    b_applied_date = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return str(self.b_name)


