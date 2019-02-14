from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from firstapp import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('firstapp/', include('firstapp.urls')),
    path('home/', user_views.home, name='home'),
    path('home1/', user_views.home1, name='home1'),
    path('register/', user_views.register, name='register'),
    # path('register/login', user_views.login, name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('bsdetails/', user_views.bsdetails, name='bsdetails'),
    path('invoiceform/', user_views.invdetails, name='invdetails'),
    path('cdetails/', user_views.cdetails, name='cdetails'),
    url(r"^inv_details/verifycustomers/(?P<bid>[0-9]+)/(?P<cid>[0-9]+)/$", user_views.verifycustomers, name='verifycustomers'),
    url(r"^inv_details/verify/submittedcustomers/(?P<bid>[0-9]+)/(?P<cid>[0-9]+)/$", user_views.submittedcustomer, name='submittedcustomer'),
    url(r"^inv_details/verifybusiness/(?P<bid>[0-9]+)/$", user_views.verifybusiness, name='verifybusiness'),
    url(r"^inv_details/verify/submittedbusiness/(?P<bid>[0-9]+)/$", user_views.submittedbusiness, name='submittedbusiness'),
    # url(r"^virtualpayment/(?P<vpa>[0-9a-zA-Z]+)/$", user_views.virtualpayment, name='VirtualPayment'),
    url(r"^repaymail/(?P<vpa>[0-9a-zA-Z]+)/(?P<b_id>[0-9]+)/(?P<c_id>[0-9]+)/$", user_views.repaymail, name='repaymail'),
]
