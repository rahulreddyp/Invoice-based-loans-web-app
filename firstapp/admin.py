from django.contrib import admin
from firstapp.models import Signup,Customer, Business

# Register your models here.
admin.site.register(Signup)
admin.site.register(Business)
admin.site.register(Customer)
