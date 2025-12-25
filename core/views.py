from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterForm

# Helper to check if user is in 'admin' group
def is_admin(user):
    return user.groups.filter(name='admin').exists()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Assign 'user' group automatically
            try:
                group = Group.objects.get(name='user')
                user.groups.add(group)
            except Group.DoesNotExist:
                pass # Prevents crash if group isn't created yet
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_page(request):
    return render(request, 'admin_page.html')