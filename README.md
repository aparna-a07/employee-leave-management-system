## 🗂️ Employee Leave Management System

A full-stack web application built with Django for managing employee leave requests within an organization.

### Features
- 🔐 Role-based login (Manager & Employee)
- 📝 Apply for Annual, Sick, and Casual leave
- ✅ Manager approval/rejection workflow with comments
- 📊 Real-time leave balance tracking
- 🔔 Notification system for request updates
- 📄 Leave history with status filters

### 🛠️ Tech Stack
- **Backend:** Python, Django 6.0
- **Frontend:** HTML, CSS, JavaScript (no frameworks)
- **Database:** SQLite3
- **Auth:** Django built-in authentication

### 🚀 Run Locally
pip install django
python manage.py migrate
python manage.py seed_data
python manage.py runserver

### 👤 Demo Accounts
| Role     | Username | Password  |
|----------|----------|-----------|
| Manager  | admin    | admin123  |
| Employee | alice    | alice123  |
| Employee | bob      | bob123    |
