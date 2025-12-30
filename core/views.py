from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import AuditLog
from django.core.exceptions import PermissionDenied

# Helper: Check if user is in 'admin' group
def is_admin(user):
    return user.groups.filter(name='admin').exists()

# REGISTER VIEW
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # AUTO-ASSIGN TO 'user' GROUP
            group, created = Group.objects.get_or_create(name='user')
            user.groups.add(group)
            
            AuditLog.objects.create(user=user, action="Account Created & Success! Login", ip_address=request.META.get('REMOTE_ADDR'))
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AuditLog.objects.create(user=user, action="Success! Login", ip_address=request.META.get('REMOTE_ADDR'))
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# DASHBOARD VIEW
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# PROFILE VIEW
@login_required
def profile_view(request):
    return render(request, 'profile.html')

# ADMIN LOGS VIEW (PROTECTED)

@login_required
def admin_page(request):
    if not is_admin(request.user):
        raise PermissionDenied # This will look for 403.html
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, 'admin_page.html', {'logs': logs})

# LOGOUT VIEW
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('dashboard')