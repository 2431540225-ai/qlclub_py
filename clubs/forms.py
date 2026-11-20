from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event, Task, Transaction


class StyledMixin:
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-control")


class RegisterForm(StyledMixin, UserCreationForm):
    student_id = forms.CharField(label="MSSV", required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


class EventForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ("title", "description", "location", "start_time")
        widgets = {"start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")}


class TaskForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "assignee", "event", "due_date")
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}


class TransactionForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ("kind", "amount", "reason", "date", "event")
        widgets = {"date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


class MinutesForm(StyledMixin, forms.Form):
    text = forms.CharField(
        label="Nội dung biên bản / ghi chú cuộc họp",
        widget=forms.Textarea(attrs={"rows": 10, "class": "form-control vaa-textarea-styled"}),
    )