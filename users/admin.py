from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _ # Добавим импорт для _

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'telegram_id', 'github_id', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'telegram_id', 'github_id']

    # Полностью переопределяем fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'avatar', 'birth_date', 'telegram_id', 'github_id')}), # Убрали first_name, last_name
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Полностью переопределяем add_fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'password2'), # Убрали first_name, last_name
        }),
        (_('Дополнительная информация'), {'fields': ('avatar', 'birth_date', 'telegram_id', 'github_id')}),
    )
