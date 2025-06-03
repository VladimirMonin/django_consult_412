# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm # UserLoginForm наследуется от AuthenticationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('landing')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) # Автоматический вход после регистрации
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
            return redirect('landing')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
    else:
        form = UserRegisterForm()
    context = {'form': form, 'title': 'Регистрация'}
    return render(request, 'users/register.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('landing')
    if request.method == 'POST':
        # AuthenticationForm принимает request как первый аргумент при инициализации с данными
        form = UserLoginForm(request, data=request.POST) 
        if form.is_valid():
            # form.get_user() возвращает аутентифицированного пользователя
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'С возвращением, {user.username}!')
            next_url = request.GET.get('next')
            return redirect(next_url or 'landing')
        else:
            # Сообщения об ошибках из AuthenticationForm (например, 'invalid_login')
            # будут обработаны в шаблоне через form.non_field_errors или field.errors
            # Дополнительно можно добавить свое сообщение, если нужно
            messages.error(request, 'Неверное имя пользователя или пароль. Попробуйте снова.')
    else:
        form = UserLoginForm() # Для GET запроса
    context = {'form': form, 'title': 'Вход'}
    return render(request, 'users/login.html', context)

@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('landing')
