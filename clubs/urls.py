from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("events/", views.event_list, name="events"),
    path("events/new/", views.event_create, name="event_create"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/qr.png", views.event_qr, name="event_qr"),
    path("events/<int:pk>/announce/", views.event_announce, name="event_announce"),
    path("checkin/<uuid:token>/", views.checkin, name="checkin"),
    path("members/", views.members, name="members"),
    path("members/<int:pk>/role/", views.change_role, name="change_role"),
    path("tasks/", views.task_list, name="tasks"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/status/", views.task_status, name="task_status"),
    path("ai/minutes/", views.minutes, name="minutes"),
]
