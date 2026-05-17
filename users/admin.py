from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ContactNickname


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_seen', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('avatar', 'bio')}),
    )


@admin.register(ContactNickname)
class ContactNicknameAdmin(admin.ModelAdmin):
    list_display = ('owner', 'contact', 'nickname')


from django.contrib import admin

# Register your models here.
