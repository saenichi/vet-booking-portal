from django.contrib import admin
from .models import Pet, Appointment

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'owner_name', 'owner_phone', 'registered_at')
    search_fields = ('name', 'owner_name')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('pet__name', 'reason')