from django.shortcuts import render, redirect, HttpResponse
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Signup, Business, Business_Invoice_Details
from django.contrib.auth.models import User
from passlib.hash import pbkdf2_sha256
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            #if not User.is_superuser:
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
    if request.method == "POST" and "apply" in request.POST:
        return render(request, 'ApplyLoan/bdetails.html', {})
    else:
        # print(request.session['_auth_user_id'])
        return render(request, 'home.html', {})

def busdetails(request):
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
        details = Business(ap_id=su, b_name=b_name, b_owner_name=b_owner_name, b_contact=b_contact, b_addr=b_addr, b_pan_no=b_pan_no, b_est_date=b_est_date, b_type=b_type)
        details.save()
        return redirect('basic')
    else:
        return render(request, 'ApplyLoan/bdetails.html')


def basic(request):
    if request.method == "POST":

        uid = request.session['_auth_user_id']
        su = Signup.objects.get(user=uid)
        bid = Business.objects.get(b_id=su.ap_id)
        b_turnover = request.POST.get('b_turnover')
        b_total_invoice_amount = request.POST.get('b_total_invoice_amount')
        b_no_of_invoices = request.POST.get('b_no_of_invoices')
        Invdetails = Business_Invoice_Details(ap_id=su, b_id=bid, b_turnover=b_turnover, b_total_invoice_amount=b_total_invoice_amount, b_no_of_invoices=b_no_of_invoices)
        Invdetails.save()
        num = int(request.POST.get("b_no_of_invoices"))
        return redirect('temp', n=num)
        #return HttpResponse("Done Adding Invoice Details")
    else:
        return render(request, 'ApplyLoan/basic.html')

def temp(request, n):
    num = int(n)
    if request.method == "POST" and num > 1:
        num = num-1
        return redirect('temp', n=num)
    elif request.method == "POST":
        return HttpResponse("Done")
    else:
        return render(request, 'ApplyLoan/form.html')
