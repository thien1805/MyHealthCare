from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Patient, Doctor
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'phone_num', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'full_name', 'phone_num']
    ordering = ["-created_at"]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Detailed information', {'fields': ('full_name', 'phone', 'role')}),
        ('Authority', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Time', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    add_fieldsets = (
        ('None', {
            'classes': ('wide',), #css để giãn chiều ngang form
            'fields': ('email', 'full_name', 'phone_num','role', 'password1', 'password2', ),
        }),
    )
    
    
# @admin.register(Patient)
# class PatientAdmin(admin.ModelAdmin):
#     list_display = ['get_full_name', 'get_email', 'date_of_birth', 'gender', 'address', 
#                     'insurance_info', 'emergency_contact', 'emergency_contact_phone',
#                     'created_at']
    