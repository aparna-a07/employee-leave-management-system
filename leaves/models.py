from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leave_balance')
    annual_leave = models.IntegerField(default=15)
    sick_leave = models.IntegerField(default=10)
    casual_leave = models.IntegerField(default=7)
    annual_used = models.IntegerField(default=0)
    sick_used = models.IntegerField(default=0)
    casual_used = models.IntegerField(default=0)

    @property
    def annual_remaining(self):
        return self.annual_leave - self.annual_used

    @property
    def sick_remaining(self):
        return self.sick_leave - self.sick_used

    @property
    def casual_remaining(self):
        return self.casual_leave - self.casual_used

    def __str__(self):
        return f"{self.user.get_full_name()} - Balance"


class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    reviewed_on = models.DateTimeField(null=True, blank=True)
    manager_comment = models.TextField(blank=True)

    @property
    def days_count(self):
        delta = self.end_date - self.start_date
        return delta.days + 1

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} ({self.status})"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    link = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.message[:40]}"
