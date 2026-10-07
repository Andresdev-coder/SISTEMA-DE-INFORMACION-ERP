from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import LoginForm, ProfileForm, StyledPasswordChangeForm
from .models import UserRole, Role

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
        
    return render(request, 'users/login.html', {'form': form})
    
@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
def profile_view(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = StyledPasswordChangeForm(request.user)

    if request.method == 'POST' and request.POST.get('form_name') == 'profile':
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Tu perfil se actualizó correctamente.')
            return redirect('profile')
    elif request.method == 'POST' and request.POST.get('form_name') == 'password':
        password_form = StyledPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña se cambió correctamente.')
            return redirect('profile')

    return render(request, 'users/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
