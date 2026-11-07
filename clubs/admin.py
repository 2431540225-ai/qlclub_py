from django.contrib import admin
from .models import Profile, Event, Attendance, Task

for m in (Profile, Event, Attendance, Task):
    admin.site.register(m)
