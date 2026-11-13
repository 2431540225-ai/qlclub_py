from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Event


class EventApplyUndoTests(TestCase):
    def setUp(self):
        self.officer_user = User.objects.create_user(username="officer", password="password")
        self.officer_user.profile.role = "officer"
        self.officer_user.profile.save()

        self.member_user = User.objects.create_user(username="member", password="password")

        self.event = Event.objects.create(
            title="Sự kiện thử nghiệm",
            description="Nội dung ban đầu",
            location="Hội trường A",
            start_time=timezone.now(),
            announcement="Nội dung AI soạn thảo hấp dẫn",
        )

    def test_apply_and_undo_announcement(self):
        self.client.login(username="officer", password="password")

        # 1. Áp dụng thông báo vào nội dung chi tiết
        apply_url = reverse("event_apply_announcement", args=[self.event.pk])
        resp = self.client.post(apply_url)
        self.assertRedirects(resp, reverse("event_detail", args=[self.event.pk]))

        self.event.refresh_from_db()
        self.assertEqual(self.event.description, "Nội dung AI soạn thảo hấp dẫn")
        self.assertEqual(self.event.previous_description, "Nội dung ban đầu")

        # 2. Hoàn tác nội dung cũ
        undo_url = reverse("event_undo_description", args=[self.event.pk])
        resp_undo = self.client.post(undo_url)
        self.assertRedirects(resp_undo, reverse("event_detail", args=[self.event.pk]))

        self.event.refresh_from_db()
        self.assertEqual(self.event.description, "Nội dung ban đầu")
        self.assertEqual(self.event.previous_description, "")

    def test_member_permission_denied(self):
        self.client.login(username="member", password="password")
        apply_url = reverse("event_apply_announcement", args=[self.event.pk])
        resp = self.client.post(apply_url)
        self.assertEqual(resp.status_code, 403)

