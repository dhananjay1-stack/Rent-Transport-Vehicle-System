from django.urls import path, include  
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
from .views import LoginView

urlpatterns = [
    path('', views.home_view, name='home'),  
    path('register/', views.register, name='register'),
    
    
    path('login/', views.LoginView, name='login'),  
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    path('accounts/profile/', views.Profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('about_us.html', views.about_us, name='about_us'),

    path('password_reset/', include('django.contrib.auth.urls')),  
    
    
    path('host_dashboard/', views.host_dashboard, name='host_dashboard'),  
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),  

    
    path('goods_carrier/create/', views.create_goods_carrier, name='create_goods_carrier'),
    path('goods_carrier/update/<int:carrier_id>/', views.update_goods_carrier, name='update_goods_carrier'),
    path('goods_carrier/delete/<int:carrier_id>/', views.delete_goods_carrier, name='delete_goods_carrier'),


    path('available_carriers/', views.available_carriers, name='available_carriers'),
   
   

    
    path('booking/<int:carrier_id>/', views.complete_booking, name='complete_booking'),
    path('booking/upi-payment/<int:booking_id>/', views.confirm_upi_payment, name='confirm_upi_payment'),

    
    path('booking/confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),

    
    path('generate_upi_qr/', views.generate_upi_qr, name='generate_upi_qr'),


    path('leave_feedback/<int:booking_id>/', views.leave_feedback, name='leave_feedback'),
    path('feedback/', views.feedback_page, name='feedback_page'),
    
    
    path('track_carrier/<int:carrier_id>/', views.track_carrier, name='track_carrier'),
    path('carrier/<int:carrier_id>/location-update/', views.carrier_location_update, name='carrier_location_update'),
    path('update-location/<int:carrier_id>/', views.carrier_location_update, name='carrier_location_update'),

]



