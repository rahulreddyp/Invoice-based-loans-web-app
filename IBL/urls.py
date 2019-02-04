from django.contrib import admin
from django.urls import path, include
from firstapp import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('firstapp/', include('firstapp.urls')),
    path('home/', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    # path('register/login', user_views.login, name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('bsdetails/', user_views.bsdetails, name='bsdetails'),
    path('invoiceform/', user_views.invdetails, name='invdetails'),
    path('cdetails/', user_views.cdetails, name='cdetails'),
]
