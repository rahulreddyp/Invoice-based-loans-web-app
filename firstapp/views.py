from django.shortcuts import render, redirect, HttpResponse
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from passlib.hash import pbkdf2_sha256
from django.conf import settings
from password import mail, password
import os, errno
import smtplib
import random
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from .models import Signup, Customer, Business, Business_Invoice_Details, B_Docs, C_Docs, StatusCustomer_LOA,\
    StatusBusiness_LOA, Loan, Investor, Accepted_Customers, Repayment, Collection, Delinquency,\
    Accepted_Business, B_Verification, C_Verification, UT_Money, VirtualPayment


# Create your views here.

k = 0
n = 0
temp = 0
number_of_invoices = ''
business_email = ''
customer_mails = []
status_cust = ''
status_bus = ''
rejected_cid = []

def register(request):
    # if not request.session.is_empty():
    # return redirect('logout')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # if not User.is_superuser:
            user = User.objects.get(username=username)
            messages.success(request, f'Account Created for {username}!')
            # name = request.POST.get('name')
            email = form.cleaned_data.get('email')
            # global business_email
            # business_email = email
            mno = form.cleaned_data.get('MobileNo')
            pwd = pbkdf2_sha256.hash(form.cleaned_data.get('password1'))
            # pwd = pbkdf2_sha256.hash("request.POST.get('pwd')")
            post = Signup(user=user, ap_name=username, ap_email=email, ap_mob=mno, ap_ip_addr="127.0.0.1", ap_pass=pwd)
            post.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    uid = request.session['_auth_user_id']
    su = Signup.objects.get(user=uid)
    # request.session.set_expiry(90)
    if request.method == "POST" and "apply" in request.POST:
        if Business.objects.filter(b_id=su.ap_id):
            return HttpResponse("You have already Submitted  your Business Details!!")
        else:
            return redirect('bsdetails')
        # (request, 'ApplyLoan/bdetails.html', {})
    elif request.method == "POST" and "resume" in request.POST:
        # su = Signup.objects.get(user=uid)
        bid = Business.objects.filter(b_id=su.ap_id)
        invid = Business_Invoice_Details.objects.filter(b_id=bid[0]).exists()
        if invid:
            return redirect('cdetails')
        elif bid:
            return redirect('invdetails')
        else:
            return HttpResponse("Sorry, You did'nt apply for any Loan. Go to Home page and Click on Apply Now!")

    else:
        return render(request, 'home.html', {})


def bsdetails(request):
    if request.method == "POST":
        uid = request.session['_auth_user_id']
        su = Signup.objects.get(user=uid)
        b_name = request.POST.get('bname')
        b_owner_name = request.POST.get('b_owner_name')
        b_email = request.POST.get('b_email')
        global business_email
        business_email = b_email
        b_contact = request.POST.get('b_contact')
        b_addr = request.POST.get('b_addr')
        b_pan_no = request.POST.get('b_pan_no')
        b_est_date = request.POST.get('b_est_date')
        b_type = request.POST.get('b_type')
        details = Business(ap_id=su, b_name=b_name, b_owner_name=b_owner_name, b_email=b_email, b_contact=b_contact,
                           b_addr=b_addr, b_pan_no=b_pan_no, b_est_date=b_est_date, b_type=b_type)
        details.save()
        request.session['ap_id'] = su.ap_id
        request.session['bid'] = details.b_id
        return redirect('home1')
    else:
        return render(request, 'ApplyLoan/bdetails.html')

@login_required
def home1(request):
    if request.method == "POST" and "resume" in request.POST:
        return redirect('invdetails')
    else:
        return render(request, 'home1.html', {})

def invdetails(request):
    global n, number_of_invoices, status_bus
    if request.method == "POST":
        uid = request.session['_auth_user_id']
        su = Signup.objects.get(user=uid)
        # bid = Business.objects.get(ap_id=su.ap_id)
        b = request.session['bid']
        print('enter' + str(b))
        bid = Business.objects.get(b_id=b)
        b_turnover = request.POST.get('b_turnover')
        b_total_invoice_amount = request.POST.get('b_total_invoice_amount')
        b_no_of_invoices = request.POST.get('b_no_of_invoices')
        invdetail = Business_Invoice_Details(ap_id=su, b_id=bid, b_turnover=b_turnover,
                                             b_total_invoice_amount=b_total_invoice_amount,
                                             b_no_of_invoices=b_no_of_invoices)
        invdetail.save()
        # Uploading Business Files
        f = request.FILES['b_file_audit']
        fname = 'b_file_audit'
        b_audit_path = b_upload(request, f, fname)
        f = request.FILES['b_file_saleledger']
        fname = 'b_file_saleledger'
        b_ledger_path = b_upload(request, f, fname)
        print('filepath in bdata::' + b_audit_path)
        document = B_Docs(ap_id=su, b_id=bid, b_file_audit=b_audit_path, b_sales_ledger=b_ledger_path)
        document.save()
        # storing b_no_of_invoices value for getting each customer Invoice's details
        number_of_invoices = int(request.POST.get("b_no_of_invoices"))
        n = number_of_invoices
        status_bus = 'Not yet Submitted'
        status_business(1, bid, request)
        return redirect('cdetails')
        # return HttpResponse("Done Adding Invoice Details")
    else:
        return render(request, 'ApplyLoan/Invoiceform.html')

# Business Files Upload
def b_upload(request, fname, filename):
    uid = request.session['_auth_user_id']
    ap_id = Signup.objects.get(user=uid)
    b_id = Business.objects.get(ap_id=ap_id.ap_id)
    # b_id = request.session['bid']
    # Creating Folder for storing User files
    new_dir_path = os.path.join(settings.MEDIA_ROOT, str(ap_id))
    try:
        os.mkdir(new_dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            # directory already exists
            pass
        else:
            print(e)
    # Creating Folder for Business files
    new_dir_path = os.path.join(new_dir_path, str(b_id))
    try:
        os.mkdir(new_dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            # directory already exists
            pass
        else:
            print(e)

    flext = str(fname).split('.')
    request.session['new_path'] = new_dir_path
    print("newpath::"+str(new_dir_path))
    fnam = str(new_dir_path) + '\\' + str(fname)
    print(fname)
    print('fnamein upload::'+fnam)
    with open(fnam, 'wb+') as destination:
        for chunk in fname.chunks():
            destination.write(chunk)
    filenew = str(new_dir_path) + '\\' + filename
    filenew = filenew + '.' + flext[1]
    os.rename(fnam, filenew)
    print(fnam+filenew)
    request.session['new_dir_path'] = new_dir_path
    return filenew


def cdetails(request):
    global n, k, customer_mails
    uid = request.session['_auth_user_id']
    su = Signup.objects.get(user=uid)
    bid = Business.objects.get(ap_id=su.ap_id)
    # Recursion for storing Individual Customer Details
    if n != 0:
        if request.method == "POST":
                c_owner_name = request.POST.get('c_owner_name')
                cb_name = request.POST.get('cb_name')
                cb_contact = request.POST.get('cb_contact')
                cb_email = request.POST.get('cb_email')
                customer_mails.append(cb_email)
                cb_address = request.POST.get('cb_address')
                cb_type = request.POST.get('c_type')
                cb_relation = request.POST.get('cb_relation')
                cb_pan_no = request.POST.get('c_bus_pan_no')
                cb_est_date = request.POST.get('c_est_date')
                cb_turnover = request.POST.get('c_turnover')
                cb_invoice_no = request.POST.get('c_invoice_no')
                cb_invoice_amt = request.POST.get('c_invoice_amount')
                c_issue_date = request.POST.get('c_invoice_issue_date')
                c_due_date = request.POST.get('c_invoice_due_date')
                custdetails = Customer(ap_id=su, b_id=bid, c_owner_name=c_owner_name, cb_name=cb_name,
                                       cb_contact=cb_contact, cb_email=cb_email, cb_address=cb_address, cb_type=cb_type,
                                       cb_relation=cb_relation, cb_pan_no=cb_pan_no,
                                       cb_est_date=cb_est_date, cb_turnover=cb_turnover,
                                       cb_invoice_no=cb_invoice_no, cb_invoice_amt=cb_invoice_amt,
                                       c_issue_date=c_issue_date, c_due_date=c_due_date)
                custdetails.save()
                request.session['c_id'] = custdetails.c_id
                # Taking required files from customers
                file_audit = request.FILES['c_file_audit']
                filename = 'c_file_audit'
                c_audit_path = c_upload(request, file_audit, filename)
                c_sales_ledger = request.FILES['c_file_saleledger']
                filename = 'c_file_saleledger'
                c_ledger_path = c_upload(request, c_sales_ledger, filename)
                c_file_invoice = request.FILES['c_file_invoice']
                filename = 'c_file_invoice'
                c_file_invoice_path = c_upload(request, c_file_invoice, filename)
                c_file_statement = request.FILES['c_file_statement']
                filename = 'c_file_statement'
                c_file_statement_path = c_upload(request, c_file_statement, filename)
                c_id = Customer.objects.get(c_id=request.session['c_id'])
                document = C_Docs(ap_id=su, b_id=bid, c_id=c_id, c_file_audit=c_audit_path,
                                  c_sales_ledger=c_ledger_path, c_file_invoice=c_file_invoice_path,
                                  c_file_statement=c_file_statement_path)
                document.save()
                # redirecting to customer files verification
                global status_cust
                status_cust = 'Not Yet Submitted'
                status_customer(1, bid, custdetails.c_id, request)
                customer_verification(bid, custdetails.c_id, request)
                print(custdetails.c_id)
                n = n - 1
                return redirect('cdetails')
        else:
            k = k + 1
            return render(request, 'ApplyLoan/customer.html', {'n': k})
    else:
        # Checking if All the customers have been rejected in ML/Manual Verification
        if C_Verification.objects.filter(b_id=bid, final_status='Accepted').count() == 0:
            business_verification(2, bid, request)
            sendemail(request, 7)
        else:
            # redirecting to the view which checks for Business accuracy in ML verification
            business_verification(1, bid, request)
        # virtualpay_mail(request)
        # sending LOA mails to customers
        sendemail(request, 1)
        return render(request, 'Status.html', {})

# Uploading customer documents in their related folders
def c_upload(request, file, filename):
    uid = request.session['_auth_user_id']
    ap_id = Signup.objects.get(user=uid)
    b_id = Business.objects.get(ap_id=ap_id.ap_id)
    # c_id = Customer.objects.get(b_id=b_id.b_id)
    # b_id = request.session['bid']
    c_id = request.session['c_id']
    new_dir_path = request.session['new_path']
    # c_id = Customer.objects.get(c_id=c_id)
    new_dir_path = os.path.join(new_dir_path, str(c_id))
    try:
        os.mkdir(new_dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            # directory already exists
            pass
        else:
            print(e)
    flext = str(file).split('.')
    print("newpath::" + str(new_dir_path))
    fnam = str(new_dir_path) + '\\' + str(file)
    print(filename)
    print('fname in upload::' + fnam)
    with open(fnam, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    filenew = str(new_dir_path) + '\\' + filename
    filenew = filenew + '.' + flext[1]
    os.rename(fnam, filenew)
    print(fnam + filenew)
    return filenew

# customer ML/Manual Verification
def customer_verification(bid, cid, request):
    global rejected_cid
    uid = request.session['_auth_user_id']
    su = Signup.objects.get(user=uid)
    cust = Customer.objects.get(c_id=cid)
    mlaccuracy = round(random.uniform(70, 100), 1)
    mvaccuracy = round(random.uniform(70, 100), 1)
    cv = C_Verification(ap_id=su, b_id=bid, c_id=cust, ml_accuracy=mlaccuracy, mv_accuracy=mvaccuracy, ml_status='Not Yet Verified', mv_status='Not Yet Verified', final_status='Not Yet Verified')
    cv.save()
    cv = C_Verification.objects.get(ap_id=su, b_id=bid, c_id=cust, ml_accuracy=mlaccuracy, mv_accuracy=mvaccuracy)
    if cv.ml_accuracy > 70:
        cv.ml_status = 'Accepted'
    else:
        cv.ml_status = 'Rejected'
    if cv.mv_accuracy > 70:
        cv.mv_status = 'Accepted'
    else:
        cv.mv_status = 'Rejected'
    if cv.ml_status == 'Accepted' and cv.mv_status == 'Accepted':
        cv.final_status = 'Accepted'
    else:
        cv.final_status = 'Rejected'
        rejected_cid.append(cid)
        customer_mails.remove(cust.cb_email)
    cv.save()
    return

def business_verification(value, bid, request):
    global number_of_invoices, rejected_cid
    uid = request.session['_auth_user_id']
    su = Signup.objects.get(user=uid)
    b = Business_Invoice_Details.objects.get(b_id=bid)
    mlaccuracy = round(random.uniform(70, 100), 1)
    mvaccuracy = round(random.uniform(70, 100), 1)
    if value == 1:
        bv = B_Verification(ap_id=su, b_id=bid, ml_accuracy=mlaccuracy, mv_accuracy=mvaccuracy, requested_amount=b.b_total_invoice_amount, sanctioned_amount=b.b_total_invoice_amount, ml_status='Not Yet Verified', mv_status = 'Not Yet Verified', final_status='Not Yet Verified')
        bv.save()
        if bv.ml_accuracy > 70:
            bv.ml_status = 'Accepted'
        else:
            bv.ml_status = 'Rejected'
        if bv.mv_accuracy > 70:
            bv.mv_status = 'Accepted'
        else:
            bv.mv_status = 'Rejected'
        if bv.ml_status == 'Accepted' and bv.mv_status == 'Accepted':
            bv.final_status = 'Accepted'
        else:
            bv.final_status = 'Rejected'
        bv.save()
        if bv.final_status == 'Accepted':
            if len(rejected_cid) == 0:
                sendemail(request, 1)
            else:
                sendemail(request, 7)
                sendemail(request, 1)

        else:
            sendemail(request, 8)
    else:
        bv = B_Verification(ap_id=su, b_id=bid, ml_accuracy=0.0, ml_remarks='Rejected due to customers',
                            mv_accuracy=0.0, mv_remarks='Rejected due to customers', requested_amount=b.b_total_invoice_amount,
                            sanctioned_amount=b.b_total_invoice_amount, ml_status='Rejected due to customers',
                            mv_status='Rejected due to customers', final_status='Rejected due to customers')
        bv.save()


# 1 send mail to all customer
# 2 send mail to business if all customers accepts
# 3 Acknowledgment email to business acceptance
# 4 send mail to business if atleast one customer accepts
# 5 Acknowledgment email to business rejection
# 6 Rejection email to business if all customers reject
# 7 Rejection email to the customers whose ML or manual verification gets rejected
# 8 Rejection email to business if ML or manual verification fails

def sendemail(request, value, smtpserver = 'smtp.gmail.com:465'):
    global customer_mails, business_email
    b = Business.objects.get(b_email=business_email)
    bid = b.b_id
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo()
    server_ssl.login(mail, password)
    if value == 1:
        for i in range(len(customer_mails)):
            c = Customer.objects.get(cb_email=customer_mails[i])
            cid = c.c_id
            text = "Hi!\nI Hope you are doing well \nHere is the link you for the accepting the LOA.Kindly do accept it before the duedate\n"+' http://127.0.0.1:8000/inv_details/verifycustomers/'+str(bid)+'/'+str(cid)
            message = 'Subject: {}\n\n{}'.format("Regarding LOA", text)
            server_ssl.sendmail(mail, [customer_mails[i]], message)
        server_ssl.close()
    if value == 2:
        text = "Hi!\nI Hope you are doing well \nAll of your customers have accepted the mail\nHere is the link you for the accepting the LOA.Kindly do accept it before the duedate\n" + ' http://127.0.0.1:8000/inv_details/verifybusiness/'+str(bid)
        message = 'Subject: {}\n\n{}'.format("Final Acceptance Mail", text)
        server_ssl.sendmail(mail, [business_email], message)
        server_ssl.close()
    if value == 3:
        text = "Hi!\nI Hope you are doing well \nThank You for accepting the aggrement. Here is a confirmation mail to say you have done the acceptance. We will shortly disburse your money\n"
        message = 'Subject: {}\n\n{}'.format("Acknowledgment Mail", text)
        server_ssl.sendmail(mail, [business_email], message)
        server_ssl.close()
        accepted_from_loa(request)
    if value == 4:
        b = Business_Invoice_Details.objects.get(b_id=bid)
        total_invoice_amount = b.b_total_invoice_amount
        text = "Hi!\nI Hope you are doing well \nThank You for accepting the agreement.Your customers with id"
        for i in range(len(rejected_cid)):
            c = Customer.objects.get(c_id=rejected_cid[i])
            total_invoice_amount -= c.cb_invoice_amt
            text += str(rejected_cid[i])+' , '
        text += "have not accepted.\nYour total loan eligibility is"+str(total_invoice_amount)+".\nHere is the link if you wish to give your decision"+' http://127.0.0.1:8000/inv_details/verifybusiness/'+str(bid)
        message = 'Subject: {}\n\n{}'.format("Final Acceptance Mail", text)
        server_ssl.sendmail(mail, [business_email], message)
        server_ssl.close()
    if value == 5:
        text = "Hi!\nI Hope you are doing well \nYou have rejected the agreement. Please create a new loan if required.\n"
        message = 'Subject: {}\n\n{}'.format("Acknowledgment Mail", text)
        server_ssl.sendmail(mail, [business_email], message)
        server_ssl.close()
    if value == 6:
        text = "Hi!\nI Hope you are doing well \nYour all customers have rejected the agreement.\n So can't provide loan.\n"
        message = 'Subject: {}\n\n{}'.format("Response Mail", text)
        server_ssl.sendmail(mail, [business_email], message)
        server_ssl.close()
    if value == 7:
        text = "Hi !\nI Hope you are doing well \nYour customer with id"
        for i in range(len(rejected_cid)):
            c = Customer.objects.get(c_id=rejected_cid[i])
            text += str(rejected_cid[i]) + ' , '
        text += "have been rejected .\n"
        message = 'Subject: {}\n\n{}'.format("Response Mail", text)
        server_ssl.sendmail(mail, [business_email], message)
        server_ssl.close()
    if value == 8:
        text = "Hi!\nI Hope you are doing well \nYour have been rejected with the loan.\n So can't provide loan.\n"
        message = 'Subject: {}\n\n{}'.format("Response Mail", text)
        server_ssl.sendmail(mail, [business_email], message)
        server_ssl.close()
    print('successfully sent the mail')

def verifycustomers(request, bid, cid):
    if request.method == 'POST':
        c = Customer.objects.get(c_id=cid)
        email = c.cb_email
        print(email)
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo()
        server_ssl.login(mail, password)
        global status_cust
        if request.POST.get('status') == 'Accepted':
            status_cust = 'Accepted'
            text = "Hi!\nI Hope you are doing well \nThank You for accepting the aggrement. Here is a confirmation mail to say you have done the acceptance.\n"
            message = 'Subject: {}\n\n{}'.format("Thank You for your agreement", text)
            server_ssl.sendmail(mail, [email], message)
            server_ssl.close()
            return redirect('submittedcustomer', bid, cid)
        else:
            rejected_cid.append(cid)
            status_cust = 'Rejected'
            text = "Hi!\nI Hope you are doing well \nYou did not accept the LOA.\n"
            message = 'Subject: {}\n\n{}'.format("Thank You for your Response", text)
            server_ssl.sendmail(mail, [email], message)
            server_ssl.close()
            return redirect('submittedcustomer', bid, cid)
    return render(request, 'LOA/loa_acceptance_mail.html')

def submittedcustomer(request, bid, cid):
    global number_of_invoices, status_bus
    status_customer(2, bid, cid, request)
    allcustomerstatus = StatusCustomer_LOA.objects.all()
    print(number_of_invoices)
    if StatusCustomer_LOA.objects.filter(b_id=bid, status='Not Yet Submitted').count() == 0:
        if StatusCustomer_LOA.objects.filter(b_id=bid, status='Accepted').count() == number_of_invoices:
            sendemail(request, 2)
        elif StatusCustomer_LOA.objects.filter(b_id=bid, status='Rejected').count() == number_of_invoices:
            status_bus = 'Rejected'
            status_business(2, bid, request)
            sendemail(request, 6)
        else:
            sendemail(request, 4)
    s = StatusCustomer_LOA.objects.get(c_id=cid)
    if s.status == 'Accepted':
        return HttpResponse('Thank you for accepting the LOA.')
    else:
        return HttpResponse('You have rejected the LOA.')

def status_customer(value, bid, cid, request):
    uid = request.session['_auth_user_id']
    status_id = Signup.objects.get(user=uid)
    cust = Customer.objects.get(c_id=cid)
    global status_cust
    if value == 1:
        st = StatusCustomer_LOA(ap_id=status_id, b_id=bid, c_id=cust, status=status_cust)
        st.save()
    else:
        st = StatusCustomer_LOA.objects.get(ap_id=status_id, b_id=bid, c_id=cust)
        st.status = status_cust
        st.save()

def verifybusiness(request, bid):
    if request.method == 'POST':
        global status_bus
        if request.POST.get('status') == 'Accepted':
            status_bus = 'Accepted'
        else:
            status_bus = 'Rejected'
        return redirect('submittedbusiness', bid)
    return render(request, 'LOA/loa_acceptance_mail.html')

def submittedbusiness(request, bid):
    status_business(2, bid, request)
    if status_bus == 'Accepted':
        sendemail(request, 3)
        return HttpResponse('Thank you for accepting the LOA.The amount will be shortly be disbursed.')
    else:
        sendemail(request, 5)
        return HttpResponse('You have rejected the loan process')

def status_business(value, bid, request):
    uid = request.session['_auth_user_id']
    status_id = Signup.objects.get(user=uid)
    if value == 1:
        st = StatusBusiness_LOA(ap_id=status_id, b_id=bid, status=status_bus)
        st.save()
    else:
        st = StatusBusiness_LOA.objects.get(ap_id=status_id, b_id=bid)
        st.status = status_bus
        st.save()

# RAHUL virtual payment for customers

# Generating virtual payment address and storing
def virtualpayment(request, b_id, c_id):
    global customer_mails
    # v_id = random.randint(100000, 999999)
    print(b_id)
    print(b_id.b_id)
    print(c_id.c_id)
    vpa = get_random_string(length=10) + str(b_id.b_id) + '/' + str(c_id.c_id)
    # cust = Customer.objects.get(c_id=c_id)
    details = VirtualPayment(vpa=vpa, b_id=b_id, c_id=c_id, expiry_date=datetime.now() + timedelta(days=10),
                             amount=c_id.cb_invoice_amt)
    details.save()
    repaymentmail(request, c_id, vpa)
    print("Disbursement process has started")

# sending virtual payment address to customer's email id
def repaymentmail(request, cust, vpa):
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo()
    server_ssl.login(mail, password)
    # c = Customer.objects.get(cb_email=)
    # virtual_payment = VirtualPayment.objects.get(c_id=c_id)
    # cid = c.c_id
    text = "Hi!" + cust.c_owner_name + "\nI Hope you are doing well \nHere is the link for paying your Invoice due amount.Kindly do it before the due date\n" + "\nhttp://127.0.0.1:8000/repaymentmail/" + str(vpa)
    message = 'Subject: {}\n\n{}'.format("Payment of Invoice Amount", text)
    server_ssl.sendmail(mail, cust.cb_email, message)
    server_ssl.close()
    print("payment mail sent")

# Customer's response page for payment
def repaymail(request, vpa, b_id, c_id):
    if request.method == 'POST':
        return HttpResponse("Payment Successful! ")
    else:
        return render(request, 'Repayment/repaymentmail.html', {})

# storing accepted business and customer details from verification
def accepted_from_loa(request):
    sb = StatusBusiness_LOA.objects.get(status='Accepted')
    accepted_business(request, sb.ap_id, sb.b_id)


# DISBURSEMENT--AJAY
def accepted_business(request, apid, bid):
    print("storing accepted business details")
    bverification = B_Verification.objects.get(b_id=bid)
    invoice_amount = bverification.requested_amount
    sanctioned_amount = bverification.sanctioned_amount
    loanid = generate_loan(request, apid, bid)
    l_id = Loan.objects.get(loan_id=loanid)
    print(l_id)
    print(l_id.loan_id)
    request.session['loanid'] = loanid
    data = Accepted_Business(ap_id=apid, b_id=bid, invoice_amount=invoice_amount, sanctioned_amount=sanctioned_amount, loan_id=l_id)
    data.save()
    sc = StatusCustomer_LOA.objects.filter(status='Accepted')
    print(sc)
    for i in sc:
        print(i.ap_id)
        accepted_customers(request, i.ap_id, i.b_id, i.c_id, loanid)
    print("loop")
    # return 'success'

def accepted_customers(request, apid, bid, cid, loan_id):
    ap_id = Signup.objects.get(ap_id=apid.ap_id)
    b_id = Business.objects.get(b_id=bid.b_id)
    cus = Customer.objects.get(c_id=cid.c_id)
    invoice_amount = cus.cb_invoice_amt
    repaid_due_date = cus.c_due_date
    loanid = Loan.objects.get(loan_id=loan_id)
    data = Accepted_Customers(ap_id=ap_id, b_id=b_id, c_id=cus, invoice_amount=invoice_amount, repaid_due_date=repaid_due_date, loan_id=loanid)
    data.save()
    print("storing customer")
    virtualpayment(request, b_id, cus)
    # return 'success'

def generate_loan(request, apid, bid):
    status = 'loan approved and id created'
    data = Loan(ap_id=apid, b_id=bid, status=status)
    data.save()
    loanid = data.loan_id
    return loanid

# def disburse(request, val):
#     loanid = request.session['loanid']
#     if val == 1:
#         a_business = Accepted_Business.objects.get(loan_id=loanid)
#         sanction_amount = a_business.sanctioned_amount
#         disburseamount = sanction_amount*0.8
#         remaining_amount = sanction_amount*0.1
#         print(disburseamount, '--', remaining_amount)
#         #Ut_Money()
#         data = Loan.objects.get(loan_id=loanid)
#         data.total_amount = sanction_amount
#         data.one_disburse_amount = disburseamount
#         data.one_disburse_date = datetime.now()
#         data.two_disburse_amount = remaining_amount
#         data.status = '1 Disbursement is completed'
#         data.save()
#     elif val == 2:
#         # a_business = accepted_business.objects.get(loan_id=loanid)
#         data = Loan.objects.get(loan_id=loanid)
#         remaining_amount = data.two_disburse_amount
#         data.two_disburse_date = datetime.now()
#         data.status = '2 Disbursement is completed'
#         data.save()
