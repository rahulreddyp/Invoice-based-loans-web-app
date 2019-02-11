from django.contrib import admin
from firstapp.models import Signup, Customer, Business, B_Docs, C_Docs,StatusCustomer, StatusBusiness

# Register your models here.
admin.site.register(Signup)
admin.site.register(Business)
admin.site.register(Customer)
admin.site.register(B_Docs)
admin.site.register(C_Docs)
admin.site.register(StatusCustomer)
admin.site.register(StatusBusiness)
