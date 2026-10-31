from django.db import models

class Pet(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    owner_name = models.CharField(max_length=100)
    owner_username = models.CharField(max_length=100, blank=True, null=True)
    owner_phone = models.CharField(max_length=20)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.species}) - Owner: {self.owner_name}"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    )

    TIME_SLOT_CHOICES = (
        ('08:00 AM', '08:00 AM - 09:00 AM'),
        ('09:00 AM', '09:00 AM - 10:00 AM'),
        ('10:00 AM', '10:00 AM - 11:00 AM'),
        ('11:00 AM', '11:00 AM - 12:00 PM'),
        ('12:00 PM', '12:00 PM - 01:00 PM'),
        ('01:00 PM', '01:00 PM - 02:00 PM'),
        ('02:00 PM', '02:00 PM - 03:00 PM'),
        ('03:00 PM', '03:00 PM - 04:00 PM'),
        ('04:00 PM', '04:00 PM - 05:00 PM'),
        ('05:00 PM', '05:00 PM - 06:00 PM'),
    )

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES, default='08:00 AM')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.pet.name} on {self.date} at {self.time_slot} [{self.status}]"