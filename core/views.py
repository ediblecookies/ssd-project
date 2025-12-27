from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from .models import AuditLog

# Logic untuk check Admin
def is_admin(user):
    return user.groups.filter(name='admin').exists()

# Signal: Rekod login berjaya
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user, 
        action="Login Berjaya", 
        ip_address=request.META.get('REMOTE_ADDR')
    )

# Signal: Rekod login gagal
@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    AuditLog.objects.create(
        user=None, 
        action=f"Login Gagal (Username: {credentials.get('username')})", 
        ip_address=request.META.get('REMOTE_ADDR')
    )

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group, created = Group.objects.get_or_create(name='user')
            user.groups.add(group)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def admin_page(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, 'admin_page.html', {'logs': logs})