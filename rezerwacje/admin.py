from django.contrib import admin
from .models import Reservations, Rooms

# Register your models here.

admin.site.register(Reservations)
admin.site.register(Rooms)