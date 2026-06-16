from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from leaves.models import LeaveBalance, LeaveRequest, Notification
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Seed demo data'

    def handle(self, *args, **kwargs):
        admin, _ = User.objects.get_or_create(username='admin')
        admin.set_password('admin123')
        admin.first_name = 'Admin'; admin.last_name = 'Manager'
        admin.email = 'admin@company.com'
        admin.is_staff = True; admin.is_superuser = True; admin.save()
        LeaveBalance.objects.get_or_create(user=admin)

        employees = [
            ('alice', 'alice123', 'Alice', 'Johnson', 'alice@company.com'),
            ('bob', 'bob123', 'Bob', 'Smith', 'bob@company.com'),
        ]
        emp_objs = []
        for uname, pwd, fn, ln, em in employees:
            u, _ = User.objects.get_or_create(username=uname)
            u.set_password(pwd); u.first_name = fn; u.last_name = ln; u.email = em
            u.is_staff = False; u.save()
            LeaveBalance.objects.get_or_create(user=u)
            emp_objs.append(u)

        alice, bob = emp_objs
        today = date.today()
        samples = [
            (alice, 'annual', today + timedelta(days=5), today + timedelta(days=9), 'Family vacation', 'pending'),
            (alice, 'sick', today - timedelta(days=10), today - timedelta(days=9), 'Fever', 'approved'),
            (bob, 'casual', today + timedelta(days=2), today + timedelta(days=2), 'Personal work', 'pending'),
            (bob, 'annual', today - timedelta(days=20), today - timedelta(days=16), 'Holiday trip', 'approved'),
        ]
        from django.utils import timezone
        for emp, lt, sd, ed, reason, status in samples:
            if not LeaveRequest.objects.filter(employee=emp, start_date=sd).exists():
                lr = LeaveRequest.objects.create(employee=emp, leave_type=lt, start_date=sd, end_date=ed, reason=reason, status=status)
                if status == 'approved':
                    bal = emp.leave_balance
                    days = (ed - sd).days + 1
                    if lt == 'annual': bal.annual_used += days
                    elif lt == 'sick': bal.sick_used += days
                    elif lt == 'casual': bal.casual_used += days
                    bal.save()
                    lr.reviewed_by = admin; lr.reviewed_on = timezone.now(); lr.save()

        Notification.objects.get_or_create(user=admin, message="Alice Johnson applied for Annual leave (5 days).")
        Notification.objects.get_or_create(user=alice, message="Your Annual leave has been approved.")
        Notification.objects.get_or_create(user=bob, message="Welcome to LeaveTrack!")
        self.stdout.write(self.style.SUCCESS('Done! Login: admin/admin123, alice/alice123, bob/bob123'))
