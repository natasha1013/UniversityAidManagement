from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

class AccountAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'role')
    list_filter = ('role', 'is_approved', 'is_active', 'is_staff')
    list_editable = ('is_approved',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Role & Status', {'fields': ('role', 'is_approved', 'is_active', 'is_staff')}),
        ('Academic Info (for Students)', {'fields': ('study_program', 'years_of_study', 'gpa')}),
        ('Organization Info (for Officers/Funders)', {'fields': ('organization_name',)}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_approved', 'is_active', 'is_staff'),
        }),
    )
    ordering = ('-created_at',)

admin.site.register(Account, AccountAdmin)