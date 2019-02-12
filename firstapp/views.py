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
    # Recursion for storing Individual Customer Details
    if n != 0:

        if request.method == "POST":

                uid = request.session['_auth_user_id']
                su = Signup.objects.get(user=uid)
                bid = Business.objects.get(ap_id=su.ap_id)
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
                global status_cust
                status_cust = 'Not Yet Submitted'
                status_customer(1, bid, custdetails.c_id, request)
                n = n-1
                return redirect('cdetails')
        else:
            k = k + 1
            return render(request, 'ApplyLoan/customer.html', {'n': k})
    else:
        sendemail(1)
        return render(request, 'Status.html', {})


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

# 1 send mail to all customer
# 2 send mail to business if all customers accepts
# 3 Acknowledgment email to business acceptance
# 4 send mail to business if atleast one customer accepts
# 5 Acknowledgment email to business rejection
# 6 Rejection email to business if all customers reject

def sendemail(value, smtpserver = 'smtp.gmail.com:465'):
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
            sendemail(2)
        elif StatusCustomer_LOA.objects.filter(b_id=bid, status='Rejected').count() == number_of_invoices:
            status_bus = 'Rejected'
            status_business(2, bid, request)
            sendemail(6)
        else:
            sendemail(4)
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
        sendemail(3)
        return HttpResponse('Thank you for accepting the LOA.The amount will be shortly be disbursed.')
    else:
        sendemail(5)
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
