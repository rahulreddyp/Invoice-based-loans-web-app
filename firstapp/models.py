from django.db import models
from django.contrib.auth.models import User
from django.forms import forms
from datetime import datetime

class Signup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ap_id = models.AutoField(primary_key=True)
    ap_name = models.TextField()
    ap_email = models.EmailField()
    ap_mob = models.CharField(max_length=12)
    ap_ip_addr = models.GenericIPAddressField(protocol='both')
    ap_pass = models.CharField(max_length=256)  # widget=forms.PasswordInput()
    ap_date = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return str(self.user)

class Business(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.AutoField(primary_key=True)
    b_name = models.CharField(max_length=30)
    b_owner_name = models.CharField(max_length=30)
    b_email = models.EmailField(default='a@example.com')
    b_contact = models.BigIntegerField(default=0)
    b_addr = models.TextField(blank=True)
    b_pan_no = models.CharField(max_length=10)
    b_est_date = models.DateField()
    b_type = models.CharField(max_length=20)
    b_applied_date = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return str(self.b_name)

class Business_Invoice_Details(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    b_turnover = models.BigIntegerField()
    b_total_invoice_amount = models.IntegerField()
    b_no_of_invoices = models.IntegerField()
    # b_status = models.CharField(max_length=30)
    # b_reject_case = models.CharField(max_length=30)

    def __str__(self):
        return str(self.b_turnover)


class Customer(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.AutoField(primary_key=True)
    c_owner_name = models.CharField(max_length=30)
    cb_name = models.CharField(max_length=30)
    # c_contact = models.BigIntegerField(default=0)
    cb_contact = models.BigIntegerField(default=0)
    cb_email = models.CharField(max_length=40)
    cb_address = models.CharField(max_length=150)
    cb_type = models.CharField(max_length=30)
    cb_relation = models.IntegerField(default=0)
    # c_pan_no = models.CharField(max_length=20)
    cb_pan_no = models.CharField(max_length=20)
    cb_est_date = models.DateTimeField(default=datetime.now, blank=True)
    cb_turnover = models.FloatField(default=0)
    cb_invoice_no = models.BigIntegerField(default=0)
    cb_invoice_amt = models.FloatField(default=0)
    c_issue_date = models.DateTimeField(blank=True)
    c_due_date = models.DateTimeField(blank=True)
    c_stored_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.cb_name)

class B_Docs(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    doc_id = models.AutoField(primary_key=True)
    b_file_audit = models.TextField(blank=True)
    b_sales_ledger = models.TextField(blank=True)

class C_Docs(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    c_file_audit = models.TextField(blank=True)
    c_sales_ledger = models.TextField(blank=True)
    c_file_invoice = models.TextField(blank=True)
    c_file_statement = models.TextField(blank=True)

class StatusCustomer_LOA(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    ap_id = models.ForeignKey(Signup, on_delete=True, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=True, blank=True)
    status = models.CharField(default='False', max_length=20)

class StatusBusiness_LOA(models.Model):
    b_id = models.ForeignKey(Business, on_delete=True, blank=True)
    ap_id = models.ForeignKey(Signup, on_delete=True, blank=True)
    status = models.CharField(default='False', max_length=20)

# Verification Table
class B_Verification(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    ml_accuracy = models.FloatField(blank=True)
    ml_status = models.CharField(default='F', max_length=1)
    ml_remarks = models.TextField(default='Not verified')
    mv_accuracy = models.CharField(default='F', max_length=1)
    mv_status = models.CharField(default='F', max_length=1)
    mv_remarks = models.TextField(default='Not verified')
    final_status = models.CharField(default='F', max_length=1)

class C_Verification(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    ml_accuracy = models.FloatField(blank=True)
    ml_status = models.CharField(default='F', max_length=1)
    ml_remarks = models.TextField(default='Not verified')
    mv_accuracy = models.FloatField(blank=True)
    mv_status = models.CharField(default='F', max_length=1)
    mv_remarks = models.TextField(default='Not verified')
    final_status = models.CharField(default='F', max_length=1)


class VirtualPayment(models.Model):
    vp_id = models.IntegerField(primary_key=True)
    vpa = models.BigIntegerField(blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    created_date = models.DateTimeField(default=datetime.now(), blank=True)
    paid_date = models.DateTimeField(blank=True)
    expiry_date = models.DateTimeField(blank=True)
    amount = models.FloatField(blank=True)

class Loan(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.AutoField(primary_key=True)
    approved_date = models.DateTimeField(default=datetime.now())
    total_amount = models.FloatField(blank=True)
    one_disburse_amount = models.FloatField(blank=True)
    one_disburse_date = models.DateTimeField(blank=True)
    two_disburse_amount = models.FloatField(blank=True)
    two_disburse_date = models.DateTimeField(blank=True)
    investor_id = models.BigIntegerField(blank=True)
    status = models.TextField(blank=True)

class Investor(models.Model):
    investor_id = models.AutoField(primary_key=True)
    amount_invested = models.FloatField(blank=True)
    amount_earned = models.FloatField(blank=True)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True)

class Accepted_Customers(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    invoice_amount = models.FloatField(blank=True)
    repaid_amount = models.FloatField(blank=True)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True)
    repaid_due_date = models.DateField(blank=True)
    repaid_paid_date = models.DateTimeField(blank=True)
    c_vpa = models.BigIntegerField(blank=True)

class Accepted_Business(models.Model):
    ap_id = models.ForeignKey(Signup, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    invoice_amount = models.FloatField(blank=True)
    sanctioned_amount = models.FloatField(blank=True)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True)
    final_paid_date = models.DateTimeField(blank=True)
    b_vpa = models.BigIntegerField(blank=True)

class Repayment(models.Model):
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Accepted_Customers, on_delete=models.CASCADE, blank=True)
    invoice_amount = models.FloatField(blank=True)
    paid_amount = models.FloatField(blank=True)
    repaid_date = models.DateTimeField(default=datetime.now(), blank=True)
    rp_status = models.CharField(default='F', max_length=1)
    rp_remarks = models.TextField()
    c_vpa = models.BigIntegerField(blank=True)

class UT_Money(models.Model):
    investor_id = models.ForeignKey(Investor, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True)
    amount_credited = models.FloatField(blank=True)
    amount_debited = models.FloatField(blank=True)
    intrst_amount = models.FloatField(blank=True)
    total_amount = models.FloatField(blank=True)

class Delinquency(models.Model):
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    c_invoice_amount = models.FloatField(blank=True)
    interest_amount = models.FloatField(blank=True)
    c_invoice_due_date = models.DateField(blank=True)
    c_invoice_paid_date = models.DateTimeField(blank=True)
    delinquency_status = models.CharField(default='False', max_length=10)

class Collection(models.Model):
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    c_invoice_amount = models.FloatField(blank=True)
    interest_amount = models.FloatField(blank=True)
    total_amount_need_pay = models.FloatField(blank=True)
    remarks = models.TextField(blank=True)
