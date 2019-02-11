from django.contrib import admin
from firstapp.models import Signup, Customer, Business, B_Docs, C_Docs, StatusCustomer, StatusBusiness, Loan,\
    Investor, Accepted_Customers, Repayment, Delinquency,\
    Accepted_Business, B_Verification, Business_Invoice_Details, C_Verification, UT_Money, VirtualPayment

# Register your models here.
admin.site.register(Signup)
admin.site.register(Business)
admin.site.register(Customer)
admin.site.register(Business_Invoice_Details)
admin.site.register(B_Docs)
admin.site.register(C_Docs)
admin.site.register(StatusCustomer)
admin.site.register(StatusBusiness)
admin.site.register(B_Verification)
admin.site.register(C_Verification)
admin.site.register(Loan)
admin.site.register(Investor)
admin.site.register(Accepted_Business)
admin.site.register(Accepted_Customers)
admin.site.register(VirtualPayment)
admin.site.register(Repayment)
admin.site.register(Delinquency)
admin.site.register(UT_Money)
