import uuid
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLES = [("admin", "Admin"), ("officer", "Ban điều hành"), ("member", "Thành viên")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLES, default="member")
    student_id = models.CharField("MSSV", max_length=20, blank=True)
    phone = models.CharField("Số điện thoại", max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_officer(self):
        return self.role in ("admin", "officer")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role="admin" if instance.is_superuser else "member")


class Event(models.Model):
    title = models.CharField("Tên sự kiện", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    location = models.CharField("Địa điểm", max_length=200)
    start_time = models.DateTimeField("Thời gian")
    announcement = models.TextField("Thông báo (AI)", blank=True)
    checkin_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendances")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")


class Task(models.Model):
    STATUS = [("todo", "Cần làm"), ("doing", "Đang làm"), ("done", "Hoàn thành")]
    title = models.CharField("Tiêu đề", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks", verbose_name="Người nhận")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sự kiện")
    due_date = models.DateField("Hạn", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="todo")

    class Meta:
        ordering = ["status", "due_date"]
