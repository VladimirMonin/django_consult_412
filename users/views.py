# users/views.py
from django.views.generic import DetailView # Добавлен DetailView
from django.contrib.auth.mixins import LoginRequiredMixin # Для CBV
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView # Добавлен PasswordChangeView
from django.views.generic.edit import CreateView, UpdateView # Добавлен UpdateView
from django.contrib.auth import login  # для автоматического входа после регистрации
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import (
    UserRegisterForm,
    UserLoginForm,
    UserProfileUpdateForm,
)  # Добавлен импорт UserProfileUpdateForm
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)  # Добавлены render, get_object_or_404
from .models import User  # Добавлен импорт модели User
from django.contrib.auth.decorators import (
    login_required,
)  # Добавлен импорт login_required
from django.contrib.auth import update_session_auth_hash # Для обновления сессии после смены пароля
from .forms import UserPasswordChangeForm # Добавлен импорт

class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("landing")  # URL для редиректа после успешного создания

    def dispatch(self, request, *args, **kwargs):
        # Перенаправляем аутентифицированных пользователей
        if request.user.is_authenticated:
            return redirect("landing")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Этот метод вызывается, когда форма валидна.
        # Сначала вызываем родительский метод для сохранения пользователя.
        response = super().form_valid(form)
        # self.object теперь содержит созданного пользователя
        user = self.object
        login(self.request, user)  # Автоматический вход
        messages.success(
            self.request,
            f"Добро пожаловать, {user.username}! Регистрация прошла успешно.",
        )
        return response  # Возвращаем HTTP-ответ (редирект на success_url)

    def form_invalid(self, form):
        messages.error(
            self.request, "Пожалуйста, исправьте ошибки в форме регистрации."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация"
        return context


class UserLoginView(LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm  # Используем нашу кастомную форму
    redirect_authenticated_user = True  # Перенаправлять, если уже авторизован

    def get_success_url(self):
        messages.success(self.request, f"С возвращением, {self.request.user.username}!")
        next_url = self.request.GET.get("next")  # Для поддержки ?next= параметра
        return next_url or reverse_lazy("landing")

    def form_invalid(self, form):
        messages.error(
            self.request, "Неверное имя пользователя или пароль. Попробуйте снова."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Вход"
        return context


class UserLogoutView(LogoutView):
    # URL для редиректа после выхода. Можно также указать в settings.LOGOUT_REDIRECT_URL
    next_page = reverse_lazy("landing")

    def dispatch(self, request, *args, **kwargs):
        # Добавляем сообщение перед выходом, если пользователь аутентифицирован
        if request.user.is_authenticated:
            messages.info(request, "Вы успешно вышли из системы.")
        return super().dispatch(request, *args, **kwargs)


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile_user' # Имя переменной в шаблоне

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object здесь это текущий profile_user
        context['title'] = f'Профиль: {self.object.username}'
        context['is_own_profile'] = (self.request.user == self.object)
        # Форма редактирования здесь не нужна, она будет на отдельной странице
        return context

class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change_form.html'
    form_class = UserPasswordChangeForm # Используем нашу кастомную форму
    # success_url будет вести на страницу профиля текущего пользователя
    
    def get_success_url(self):
        messages.success(self.request, 'Ваш пароль был успешно изменен.')
        # После смены пароля перенаправляем на страницу просмотра своего профиля
        return reverse_lazy('users:profile_detail', kwargs={'pk': self.request.user.pk})

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки при смене пароля.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Смена пароля'
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileUpdateForm # Используем существующую форму
    template_name = 'users/profile_update_form.html' # Новый шаблон для формы редактирования
    # context_object_name = 'user_profile' # Можно задать, если нужно другое имя в шаблоне

    def get_object(self, queryset=None):
        # UpdateView будет редактировать только текущего пользователя
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Ваш профиль успешно обновлен.')
        # После обновления перенаправляем на страницу просмотра своего профиля
        return reverse_lazy('users:profile_detail', kwargs={'pk': self.request.user.pk})

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'
        return context
