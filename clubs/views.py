import io
from functools import wraps

import qrcode
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .ai import draft_announcement, summarize_minutes
from .forms import EventForm, MinutesForm, RegisterForm, TaskForm
from .models import Attendance, Event, Task


def role_required(*roles):
    def deco(view):
        @wraps(view)
        @login_required
        def wrapper(request, *a, **k):
            if request.user.profile.role not in roles:
                raise PermissionDenied
            return view(request, *a, **k)
        return wrapper
    return deco


OFFICER = ("admin", "officer")


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        user.profile.student_id = form.cleaned_data["student_id"]
        user.profile.save()
        login(request, user)
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


@login_required
def home(request):
    ctx = {
        "upcoming": Event.objects.filter(start_time__gte=timezone.now())[:5],
        "my_tasks": Task.objects.filter(assignee=request.user).exclude(status="done")[:5],
        "n_members": User.objects.count(),
        "n_events": Event.objects.count(),
        "n_attended": Attendance.objects.filter(user=request.user).count(),
    }
    return render(request, "clubs/home.html", ctx)


@login_required
def event_list(request):
    return render(request, "clubs/event_list.html", {"events": Event.objects.all()})


@role_required(*OFFICER)
def event_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        ev = form.save(commit=False)
        ev.created_by = request.user
        ev.save()
        messages.success(request, "Đã tạo sự kiện.")
        return redirect("event_detail", pk=ev.pk)
    return render(request, "clubs/form.html", {"form": form, "title": "Tạo sự kiện"})


@login_required
def event_detail(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    ctx = {
        "event": ev,
        "attendances": ev.attendances.select_related("user"),
        "checked_in": ev.attendances.filter(user=request.user).exists(),
    }
    return render(request, "clubs/event_detail.html", ctx)


@role_required(*OFFICER)
def event_qr(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    url = request.build_absolute_uri(reverse("checkin", args=[ev.checkin_token]))
    buf = io.BytesIO()
    qrcode.make(url).save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


@login_required
def checkin(request, token):
    ev = get_object_or_404(Event, checkin_token=token)
    _, created = Attendance.objects.get_or_create(event=ev, user=request.user)
    messages.success(request, "Điểm danh thành công!" if created else "Bạn đã điểm danh sự kiện này rồi.")
    return redirect("event_detail", pk=ev.pk)


@role_required(*OFFICER)
@require_POST
def event_announce(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    ev.announcement = draft_announcement(ev)
    ev.save()
    return redirect("event_detail", pk=ev.pk)


@role_required(*OFFICER)
def members(request):
    return render(request, "clubs/members.html", {"users": User.objects.select_related("profile").order_by("username")})


@role_required("admin")
@require_POST
def change_role(request, pk):
    u = get_object_or_404(User, pk=pk)
    role = request.POST.get("role")
    if role in ("admin", "officer", "member"):
        u.profile.role = role
        u.profile.save()
        messages.success(request, f"Đã đổi vai trò của {u.username}.")
    return redirect("members")


@login_required
def task_list(request):
    qs = Task.objects.select_related("assignee", "event")
    if not request.user.profile.is_officer:
        qs = qs.filter(assignee=request.user)
    return render(request, "clubs/task_list.html", {"tasks": qs, "statuses": Task.STATUS})


@role_required(*OFFICER)
def task_create(request):
    form = TaskForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Đã giao task.")
        return redirect("tasks")
    return render(request, "clubs/form.html", {"form": form, "title": "Giao task"})


@login_required
@require_POST
def task_status(request, pk):
    t = get_object_or_404(Task, pk=pk)
    if t.assignee != request.user and not request.user.profile.is_officer:
        raise PermissionDenied
    if request.POST.get("status") in dict(Task.STATUS):
        t.status = request.POST["status"]
        t.save()
    return redirect("tasks")


@role_required(*OFFICER)
def minutes(request):
    form = MinutesForm(request.POST or None)
    result = None
    if form.is_valid():
        roles = ", ".join(f"{u.username} ({u.profile.get_role_display()})" for u in User.objects.select_related("profile"))
        result = summarize_minutes(form.cleaned_data["text"], roles)
    return render(request, "clubs/minutes.html", {"form": form, "result": result})
