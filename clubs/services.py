from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.utils import timezone

from .models import Attendance, Event, Task, Transaction

User = get_user_model()


def engagement_report(days=60):
    """Thống kê mức độ tương tác của từng thành viên trong `days` ngày gần nhất."""
    now = timezone.now()
    events = Event.objects.filter(
        start_time__gte=now - timedelta(days=days),
        start_time__lte=now,
    )
    total = events.count()

    users = User.objects.filter(is_active=True).annotate(
        attended=Count(
            "attendance",
            filter=Q(attendance__event__in=events),
            distinct=True,
        ),
        overdue=Count(
            "tasks",
            filter=Q(tasks__due_date__lt=timezone.localdate()) & ~Q(tasks__status="done"),
            distinct=True,
        ),
    )

    rows = []
    for u in users:
        rate = u.attended / total if total else None
        low = total >= 3 and (rate < 0.3 or u.overdue >= 2)
        rows.append({
            "user": u,
            "attended": u.attended,
            "total": total,
            "rate": rate,
            "overdue": u.overdue,
            "low": low,
        })
    return rows


def activity_report(days=90):
    """Báo cáo tổng hợp hoạt động CLB trong `days` ngày gần nhất."""
    now = timezone.now()
    today = timezone.localdate()
    since = now - timedelta(days=days)
    since_date = timezone.localtime(since).date()

    events = Event.objects.filter(start_time__gte=since, start_time__lte=now)
    n_events = events.count()
    n_members = User.objects.filter(is_active=True).count()
    n_attend = Attendance.objects.filter(event__in=events).count()
    attend_pct = round(n_attend * 100 / (n_events * n_members)) if n_events and n_members else None
    top_events = events.annotate(n=Count("attendances")).order_by("-n")[:5]

    status = dict(Task.objects.values_list("status").annotate(n=Count("id")))
    n_tasks = sum(status.values())
    done = status.get("done", 0)
    overdue = Task.objects.filter(due_date__lt=today).exclude(status="done").count()

    agg = Transaction.objects.filter(date__gte=since_date).aggregate(
        income=Sum("amount", filter=Q(kind="income")),
        expense=Sum("amount", filter=Q(kind="expense")),
    )
    all_agg = Transaction.objects.aggregate(
        income=Sum("amount", filter=Q(kind="income")),
        expense=Sum("amount", filter=Q(kind="expense")),
    )

    return {
        "n_events": n_events,
        "n_members": n_members,
        "n_attend": n_attend,
        "attend_pct": attend_pct,
        "top_events": top_events,
        "n_tasks": n_tasks,
        "tasks_todo": status.get("todo", 0),
        "tasks_doing": status.get("doing", 0),
        "tasks_done": done,
        "tasks_overdue": overdue,
        "done_pct": round(done * 100 / n_tasks) if n_tasks else None,
        "income": agg["income"] or 0,
        "expense": agg["expense"] or 0,
        "balance": (all_agg["income"] or 0) - (all_agg["expense"] or 0),
        "n_low": sum(1 for r in engagement_report(days) if r["low"]),
    }