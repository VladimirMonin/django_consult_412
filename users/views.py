# users/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.contrib.auth import login # для автоматического входа после регистрации
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm # Добавлен импорт UserProfileUpdateForm
from django.shortcuts import redirect, render, get_object_or_404 # Добавлены render, get_object_or_404
from .models import User # Добавлен импорт модели User
from django.contrib.auth.decorators import login_required # Добавлен импорт login_required

class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('landing') # URL для редиректа после успешного создания

    def dispatch(self, request, *args, **kwargs):
        # Перенаправляем аутентифицированных пользователей
        if request.user.is_authenticated:
            return redirect('landing')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Этот метод вызывается, когда форма валидна.
        # Сначала вызываем родительский метод для сохранения пользователя.
        response = super().form_valid(form) 
        # self.object теперь содержит созданного пользователя
        user = self.object 
        login(self.request, user) # Автоматический вход
        messages.success(self.request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
        return response # Возвращаем HTTP-ответ (редирект на success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm # Используем нашу кастомную форму
    redirect_authenticated_user = True # Перенаправлять, если уже авторизован

    def get_success_url(self):
        messages.success(self.request, f'С возвращением, {self.request.user.username}!')
        next_url = self.request.GET.get('next') # Для поддержки ?next= параметра
        return next_url or reverse_lazy('landing')

    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль. Попробуйте снова.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context

class UserLogoutView(LogoutView):
    # URL для редиректа после выхода. Можно также указать в settings.LOGOUT_REDIRECT_URL
    next_page = reverse_lazy('landing') 

    def dispatch(self, request, *args, **kwargs):
        # Добавляем сообщение перед выходом, если пользователь аутентифицирован
        if request.user.is_authenticated:
             messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)

@login_required
def profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    is_own_profile = (request.user == profile_user)

    if is_own_profile:
        if request.method == 'POST':
            form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile_user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ваш профиль успешно обновлен.')
                return redirect('users:profile_detail', user_id=profile_user.id)
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
        else:
            form = UserProfileUpdateForm(instance=profile_user)
        
        context = {
            'title': f'Профиль: {profile_user.username}',
            'profile_user': profile_user,
            'form': form,
            'is_own_profile': is_own_profile,
        }
        return render(request, 'users/profile_detail.html', context)
    else:
        # Просмотр чужого профиля
        context = {
            'title': f'Профиль: {profile_user.username}',
            'profile_user': profile_user,
            'is_own_profile': is_own_profile,
        }
        return render(request, 'users/profile_detail.html', context)
