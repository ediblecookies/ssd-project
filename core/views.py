from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import AuditLog

# --- CUSTOM REGISTRATION FORM ---
# This class handles the email field and role selection requirement
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    
    ROLE_CHOICES = [
        ('user', 'Standard User'),
        ('admin', 'Administrator'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        required=True, 
        label="Select Role",
        widget=forms.Select(attrs={'class': 'role-selector'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

# --- VIEWS ---

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save() # Automatic Password Hashing
            role_name = form.cleaned_data.get('role')
            
            # RBAC: Assigning user to the selected group
            group, created = Group.objects.get_or_create(name=role_name)
            user.groups.add(group)
            
            # Audit Logging
            AuditLog.objects.create(
                user=user, 
                action=f"CREATE: Account created as {role_name.upper()}", 
                ip_address=request.META.get('REMOTE_ADDR')
            )
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AuditLog.objects.create(user=user, action="LOGIN_SUCCESS", ip_address=request.META.get('REMOTE_ADDR'))
            return redirect('dashboard')
        else:
            AuditLog.objects.create(user=None, action="LOGIN_FAIL", ip_address=request.META.get('REMOTE_ADDR'))
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# --- THIS WAS THE MISSING FUNCTION CAUSING THE ERROR ---
@login_required
def profile_view(request):
    return render(request, 'profile.html')

@login_required
def admin_page(request):
    # RBAC Security Check
    if not request.user.groups.filter(name='admin').exists():
        AuditLog.objects.create(
            user=request.user, 
            action="UNAUTHORIZED_ACCESS_ATTEMPT", 
            ip_address=request.META.get('REMOTE_ADDR')
        )
        raise PermissionDenied # Redirects to your custom 403.html
    
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, 'admin_page.html', {'logs': logs})

def logout_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            AuditLog.objects.create(user=request.user, action="LOGOUT", ip_address=request.META.get('REMOTE_ADDR'))
        logout(request)
        return redirect('login')
    return redirect('dashboard')