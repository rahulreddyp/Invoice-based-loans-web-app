from django.contrib import admin
from django.urls import path, include
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
    path("basic/upload_books/verifycustomers", user_views.verifycustomers, name='verifycustomers'),
    path("basic/upload_books/verify/submittedcustomers", user_views.submittedcustomer, name='submittedcustomer'),
    path("basic/upload_books/verifybusiness", user_views.verifybusiness, name='verifybusiness'),
    path("basic/upload_books/verify/submittedbusiness",user_views.submittedbusiness, name='submittedbusiness'),

]
