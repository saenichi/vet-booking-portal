from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('register-pet/', views.register_pet_view, name='register_pet'),
    path('book-appointment/', views.book_appointment_view, name='book_appointment'),
    path('staff-portal/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff-portal/pets/', views.staff_pets_view, name='staff_pets'),
    path('staff-portal/appointments/', views.staff_appointments_view, name='staff_appointments'),
    path('approve/<int:pk>/', views.approve_appointment_view, name='approve_appointment'),
    path('contact/', views.contact_us_view, name='contact_us'),
    path('services/', views.services_view, name='services'),
]