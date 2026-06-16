from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from .models import LeaveRequest, LeaveBalance, Notification
import json


def create_notification(user, message, link=''):
    Notification.objects.create(user=user, message=message, link=link)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'leaves/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    try:
        balance = user.leave_balance
    except LeaveBalance.DoesNotExist:
        balance = LeaveBalance.objects.create(user=user)

    my_requests = LeaveRequest.objects.filter(employee=user).order_by('-applied_on')[:5]
    unread_count = user.notifications.filter(is_read=False).count()

    # Manager sees pending requests
    pending_for_review = []
    if user.is_staff:
        pending_for_review = LeaveRequest.objects.filter(status='pending').order_by('-applied_on')[:10]

    context = {
        'balance': balance,
        'my_requests': my_requests,
        'pending_for_review': pending_for_review,
        'unread_count': unread_count,
        'is_manager': user.is_staff,
    }
    return render(request, 'leaves/dashboard.html', context)


@login_required
def apply_leave(request):
    user = request.user
    try:
        balance = user.leave_balance
    except LeaveBalance.DoesNotExist:
        balance = LeaveBalance.objects.create(user=user)

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        from datetime import date
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        if end < start:
            messages.error(request, 'End date must be after start date.')
            return redirect('apply_leave')

        days = (end - start).days + 1

        # Check balance
        remaining = {'annual': balance.annual_remaining, 'sick': balance.sick_remaining, 'casual': balance.casual_remaining}
        if days > remaining.get(leave_type, 0):
            messages.error(request, f'Insufficient {leave_type} leave balance. You have {remaining.get(leave_type, 0)} days remaining.')
            return redirect('apply_leave')

        leave = LeaveRequest.objects.create(
            employee=user,
            leave_type=leave_type,
            start_date=start,
            end_date=end,
            reason=reason,
        )

        # Notify managers
        managers = User.objects.filter(is_staff=True)
        for mgr in managers:
            create_notification(mgr, f"{user.get_full_name()} applied for {leave_type} leave ({days} days).", f"/leaves/{leave.id}/")

        messages.success(request, 'Leave request submitted successfully!')
        return redirect('my_leaves')

    return render(request, 'leaves/apply_leave.html', {'balance': balance})


@login_required
def my_leaves(request):
    status_filter = request.GET.get('status', '')
    qs = LeaveRequest.objects.filter(employee=request.user).order_by('-applied_on')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'leaves/my_leaves.html', {'leaves': qs, 'status_filter': status_filter})


@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if leave.employee != request.user and not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return render(request, 'leaves/leave_detail.html', {'leave': leave})


@login_required
def cancel_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk, employee=request.user)
    if leave.status == 'pending':
        leave.status = 'cancelled'
        leave.save()
        messages.success(request, 'Leave request cancelled.')
    else:
        messages.error(request, 'Only pending requests can be cancelled.')
    return redirect('my_leaves')


@login_required
def review_leave(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    leave = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')

        if action in ('approved', 'rejected') and leave.status == 'pending':
            leave.status = action
            leave.reviewed_by = request.user
            leave.reviewed_on = timezone.now()
            leave.manager_comment = comment
            leave.save()

            if action == 'approved':
                bal = leave.employee.leave_balance
                if leave.leave_type == 'annual':
                    bal.annual_used += leave.days_count
                elif leave.leave_type == 'sick':
                    bal.sick_used += leave.days_count
                elif leave.leave_type == 'casual':
                    bal.casual_used += leave.days_count
                bal.save()

            create_notification(
                leave.employee,
                f"Your {leave.leave_type} leave request has been {action}." + (f" Comment: {comment}" if comment else ""),
                f"/leaves/{leave.id}/"
            )
            messages.success(request, f'Leave request {action}.')

    return redirect('all_leaves')


@login_required
def all_leaves(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    status_filter = request.GET.get('status', '')
    qs = LeaveRequest.objects.all().order_by('-applied_on')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'leaves/all_leaves.html', {'leaves': qs, 'status_filter': status_filter})


@login_required
def notifications_view(request):
    notifs = request.user.notifications.all()
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'leaves/notifications.html', {'notifications': notifs})


@login_required
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
def notification_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})
