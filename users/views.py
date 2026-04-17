from django.utils import timezone
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login as auth_login, logout
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login_page")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()        
    return render(request, "users/register.html", {"form": form})


def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        form = LoginForm(request, data = request.POST)

        if form.is_valid():
            user = form.get_user()
            user.is_online = True
            user.last_seen = timezone.now()
            user.save(update_fields=["is_online", "last_seen"])

            auth_login(request, user)
            
            return redirect("home")
        
        else:
            messages.error(request, "Invalid email or password")

    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    user = request.user
    if user.is_authenticated:
        user.is_online = False
        user.last_seen = timezone.now()
        user.save(update_fields=["is_online", "last_seen"])

    logout(request)
    return redirect('login_page')
        
@login_required
def home(request):
    return render(request, "users/home.html")