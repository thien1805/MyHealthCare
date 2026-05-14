from django.contrib import admin
from .models import Department, Service, Room, Appointment


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon', 'health_examination_fee', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'department', 'price', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['department', 'name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_number', 'floor', 'department', 'is_active', 'created_at']
    list_filter = ['floor', 'department', 'is_active']
    search_fields = ['room_number', 'department']
    list_editable = ['is_active']
    ordering = ['floor', 'room_number']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'patient',
        'doctor',
        'service',
        'appointment_date',
        'appointment_time',
        'status',
        'estimated_fee',
        'created_at'
    ]
    list_filter = ['status', 'appointment_date', 'created_at', 'department', 'service']
    search_fields = [
        'patient__full_name',
        'patient__email',
        'doctor__full_name',
        'doctor__email',
        'department__name',
        'service__name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']
    date_hierarchy = 'appointment_date'
    ordering = ['-appointment_date', 'appointment_time']
    
    fieldsets = (
        ('Appointment Information', {
            'fields': ('patient', 'doctor', 'department', 'service', 'room')
        }),
        ('Schedule', {
            'fields': ('appointment_date', 'appointment_time', 'status')
        }),
        ('Details', {
            'fields': ('symptoms', 'reason', 'notes', 'estimated_fee')
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Reschedule', {
            'fields': ('rescheduled_from',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
