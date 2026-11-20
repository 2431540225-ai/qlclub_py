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
    path("events/<int:pk>/apply-announcement/", views.event_apply_announcement, name="event_apply_announcement"),
    path("events/<int:pk>/undo-description/", views.event_undo_description, name="event_undo_description"),
    path("checkin/<uuid:token>/", views.checkin, name="checkin"),
    path("members/", views.members, name="members"),
    path("members/<int:pk>/role/", views.change_role, name="change_role"),
    path("tasks/", views.task_list, name="tasks"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/status/", views.task_status, name="task_status"),
    path("ai/minutes/", views.minutes, name="minutes"),
    path("ai/minutes/apply/", views.minutes_apply_tasks, name="minutes_apply_tasks"),
    path("reports/engagement/", views.engagement, name="engagement"),
    path("reports/activity/", views.report, name="report"),
    path("fund/", views.fund, name="fund"),
    path("fund/new/", views.transaction_create, name="transaction_create"),
    path("fund/<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
]