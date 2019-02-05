from django.shortcuts import render, redirect, HttpResponse
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Signup, Business, Business_Invoice_Details, Customer
from django.contrib.auth.models import User
from passlib.hash import pbkdf2_sha256
# Create your views here.

n = ''
k = 0
def register(request):
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
    # request.session.set_expiry(90)
    if request.method == "POST" and "apply" in request.POST:
        return redirect('bsdetails')
        # (request, 'ApplyLoan/bdetails.html', {})
    else:
        return render(request, 'home.html', {})

def bsdetails(request):
    if request.method == "POST":
        uid = request.session['_auth_user_id']
        su = Signup.objects.get(user=uid)
        b_name = request.POST.get('bname')
        b_owner_name = request.POST.get('b_owner_name')
        b_contact = request.POST.get('b_contact')
        b_addr = request.POST.get('b_addr')
        b_pan_no = request.POST.get('b_pan_no')
        b_est_date = request.POST.get('b_est_date')
        b_type = request.POST.get('b_type')
        details = Business(ap_id=su, b_name=b_name, b_owner_name=b_owner_name, b_contact=b_contact, b_addr=b_addr,
                           b_pan_no=b_pan_no, b_est_date=b_est_date, b_type=b_type)
        details.save()
        return redirect('invdetails')
    else:
        return render(request, 'ApplyLoan/bdetails.html')


def invdetails(request):
    global n, k
    if request.method == "POST":

        uid = request.session['_auth_user_id']
        su = Signup.objects.get(user=uid)
        bid = Business.objects.get(ap_id=su.ap_id)
        # temp = bid.b_id
        b_turnover = request.POST.get('b_turnover')
        b_total_invoice_amount = request.POST.get('b_total_invoice_amount')
        b_no_of_invoices = request.POST.get('b_no_of_invoices')
        invdetail = Business_Invoice_Details(ap_id=su, b_id=bid, b_turnover=b_turnover, b_total_invoice_amount=b_total_invoice_amount, b_no_of_invoices=b_no_of_invoices)
        invdetail.save()
        # storing b_no_of_invoices value for getting each customer Invoice's details
        n = int(request.POST.get("b_no_of_invoices"))
        # Storing global variable n value into k for future reference
        k = n
        return redirect('cdetails')
        # return HttpResponse("Done Adding Invoice Details")
    else:
        return render(request, 'ApplyLoan/Invoiceform.html')

def cdetails(request):
    global n, k
    # Recursion for storing Individual Customer Details
    if n != 0:
        temp = int(k/n)
        if request.method == "POST":

                uid = request.session['_auth_user_id']
                su = Signup.objects.get(user=uid)
                bid = Business.objects.get(ap_id=su.ap_id)
                c_owner_name = request.POST.get('c_owner_name')
                cb_name = request.POST.get('cb_name')
                cb_contact = request.POST.get('cb_contact')
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
                                       cb_contact=cb_contact, cb_address=cb_address, cb_type=cb_type,
                                       cb_relation=cb_relation, cb_pan_no=cb_pan_no,
                                       cb_est_date=cb_est_date, cb_turnover=cb_turnover,
                                       cb_invoice_no=cb_invoice_no, cb_invoice_amt=cb_invoice_amt,
                                       c_issue_date=c_issue_date, c_due_date=c_due_date)
                custdetails.save()
                n = n-1
                return redirect('cdetails')
        else:
            return render(request, 'ApplyLoan/customer.html', {'n': temp})
    else:
        return render(request, 'Status.html', {})
