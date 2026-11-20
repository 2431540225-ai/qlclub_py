from django.contrib import admin
from .models import Profile, Event, Attendance, Task, Transaction

for m in (Profile, Event, Attendance, Task, Transaction):
    admin.site.register(m)