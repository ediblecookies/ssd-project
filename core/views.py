from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test

# This checks if the user is in the 'admin' group
def is_admin(user):
    return user.groups.filter(name='admin').exists()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically put new signups into the 'user' group
            group, created = Group.objects.get_or_create(name='user')
            user.groups.add(group)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# This page is PROTECTED. Only admins can enter.
@login_required
@user_passes_test(is_admin, login_url='dashboard')
def admin_page(request):
    return render(request, 'admin_page.html')