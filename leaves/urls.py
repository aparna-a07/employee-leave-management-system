from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('my-leaves/', views.my_leaves, name='my_leaves'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leaves/<int:pk>/cancel/', views.cancel_leave, name='cancel_leave'),
    path('leaves/<int:pk>/review/', views.review_leave, name='review_leave'),
    path('all-leaves/', views.all_leaves, name='all_leaves'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_read'),
    path('notifications/count/', views.notification_count, name='notif_count'),
]
