from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
import json
from .models import Pet, Appointment
from .forms import UserRegistrationForm, PetRegistrationForm, AppointmentBookingForm, UserInfoUpdateForm, UserPasswordChangeForm

def is_staff_user(user):
    return user.is_staff

def login_view(request):
    if request.user.is_authenticated:
        return redirect('staff_dashboard' if request.user.is_staff else 'dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('staff_dashboard' if user.is_staff else 'dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'pets/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'pets/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile_update_view(request):
    info_form = UserInfoUpdateForm(instance=request.user)
    password_form = UserPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_info' in request.POST:
            info_form = UserInfoUpdateForm(request.POST, instance=request.user)
            if info_form.is_valid():
                info_form.save()
                messages.success(request, "Account information updated successfully!")
                return redirect('profile_update')
        elif 'update_password' in request.POST:
            password_form = UserPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                new_pwd = password_form.cleaned_data.get('new_password')
                request.user.set_password(new_pwd)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password updated successfully!")
                return redirect('profile_update')

    return render(request, 'pets/profile_update.html', {
        'info_form': info_form,
        'password_form': password_form
    })

@login_required(login_url='login')
def dashboard_view(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
   
    user_pets = Pet.objects.filter(
        Q(owner_username__iexact=request.user.username) |
        Q(owner_name__iexact=request.user.username) |
        Q(owner_name__iexact=request.user.get_full_name())
    ).distinct()
   
    user_appointments = Appointment.objects.filter(pet__in=user_pets).order_by('-date')
    full_name = request.user.get_full_name() or request.user.username

    return render(request, 'pets/dashboard.html', {
        'my_pets': user_pets,
        'my_appointments': user_appointments,
        'full_name': full_name
    })

@login_required(login_url='login')
def register_pet_view(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
   
    default_owner = request.user.get_full_name() or request.user.username
    pet_form = PetRegistrationForm(initial={'owner_name': default_owner})
   
    if request.method == 'POST':
        pet_form = PetRegistrationForm(request.POST)
        if pet_form.is_valid():
            pet = pet_form.save(commit=False)
            pet.owner_username = request.user.username
            pet.owner_name = default_owner
            pet.save()
            messages.success(request, f"Pet '{pet.name}' successfully registered under your account!")
            return redirect('dashboard')
    return render(request, 'pets/register_pet.html', {'pet_form': pet_form})

@login_required(login_url='login')
def book_appointment_view(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
   
    user_pets = Pet.objects.filter(
        Q(owner_username__iexact=request.user.username) |
        Q(owner_name__iexact=request.user.username) |
        Q(owner_name__iexact=request.user.get_full_name())
    ).distinct()
   
    user_appointments = Appointment.objects.filter(pet__in=user_pets).order_by('-date')
    appointment_form = AppointmentBookingForm()
    appointment_form.fields['pet'].queryset = user_pets

    if request.method == 'POST':
        appointment_form = AppointmentBookingForm(request.POST)
        appointment_form.fields['pet'].queryset = user_pets
       
        if appointment_form.is_valid():
            chosen_date = appointment_form.cleaned_data.get('date')
            chosen_slot = appointment_form.cleaned_data.get('time_slot')
           
            daily_total = Appointment.objects.filter(date=chosen_date, status='Approved').count()
            slot_total = Appointment.objects.filter(date=chosen_date, time_slot=chosen_slot, status='Approved').count()
           
            if daily_total >= 200:
                messages.error(request, f"The date {chosen_date} has reached the maximum limit of 200 patients.")
            elif slot_total >= 10:
                messages.error(request, f"The time slot {chosen_slot} on {chosen_date} is fully booked (10/10 capacity).")
            else:
                appointment = appointment_form.save(commit=False)
                appointment.status = 'Pending'
                appointment.save()
                messages.success(request, f"Appointment requested for {chosen_date} at {chosen_slot}! Pending staff review.")
                return redirect('book_appointment')
                
    return render(request, 'pets/book_appointment.html', {
        'appointment_form': appointment_form,
        'user_appointments': user_appointments,
        'user_pets': user_pets
    })

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='dashboard')
def staff_dashboard_view(request):
    pending_appointments = Appointment.objects.filter(status='Pending').order_by('-date')

    # Database Metrics for Dashboard Cards
    total_pets = Pet.objects.count()
    total_appointments = Appointment.objects.count()
    total_pending = Appointment.objects.filter(status='Pending').count()
    total_approved = Appointment.objects.filter(status='Approved').count()

    # Pass approved appointments data into JSON format for the interactive Calendar View
    approved_appts = Appointment.objects.filter(status='Approved').select_related('pet')
    calendar_events = []
    for appt in approved_appts:
        calendar_events.append({
            'date': str(appt.date),
            'pet_name': appt.pet.name,
            'species': appt.pet.species,
            'owner_name': appt.pet.owner_name,
            'time_slot': appt.time_slot,
            'reason': appt.reason
        })

    return render(request, 'pets/staff_dashboard.html', {
        'pending_appointments': pending_appointments,
        'total_pets': total_pets,
        'total_appointments': total_appointments,
        'total_pending': total_pending,
        'total_approved': total_approved,
        'calendar_events_json': json.dumps(calendar_events)
    })

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='dashboard')
def staff_pets_view(request):
    search_query = request.GET.get('search', '').strip()
    pets = Pet.objects.all().order_by('-registered_at')

    if search_query:
        pets = pets.filter(
            Q(name__icontains=search_query) |
            Q(owner_name__icontains=search_query) |
            Q(species__icontains=search_query)
        )

    return render(request, 'pets/staff_pets.html', {
        'pets': pets,
        'search_query': search_query
    })

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='dashboard')
def staff_appointments_view(request):
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    appointments = Appointment.objects.all().order_by('-date')

    if search_query:
        appointments = appointments.filter(
            Q(pet__name__icontains=search_query) |
            Q(pet__owner_name__icontains=search_query) |
            Q(date__icontains=search_query) |
            Q(time_slot__icontains=search_query) |
            Q(reason__icontains=search_query)
        )

    if status_filter:
        appointments = appointments.filter(status__iexact=status_filter)

    return render(request, 'pets/staff_appointments.html', {
        'appointments': appointments,
        'search_query': search_query,
        'status_filter': status_filter
    })

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='dashboard')
def approve_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    slot_total = Appointment.objects.filter(date=appointment.date, time_slot=appointment.time_slot, status='Approved').count()
   
    if slot_total >= 10:
        messages.error(request, f"Cannot approve. The {appointment.time_slot} slot on {appointment.date} reached max 10 limit.")
    else:
        appointment.status = 'Approved'
        appointment.save()
        messages.success(request, f"Appointment for {appointment.pet.name} approved successfully.")
    return redirect('staff_dashboard')

@login_required(login_url='login')
def contact_us_view(request):
    return render(request, 'pets/contact.html')

@login_required(login_url='login')
def services_view(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
    return render(request, 'pets/services.html')