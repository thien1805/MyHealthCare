from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Department(models.Model):
    """
    Department model - Medical departments/specialties
    Chứa các services
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Department name (e.g., 'Nhi khoa', 'Tim mạch')"
    )
    icon = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Emoji/icon for UI display (e.g., '👶', '❤️')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Department description"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this department is active"
    )
    health_examination_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Health examination fee in VND")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Service(models.Model):
    """
    Service model - Medical services
    Belongs to a Department
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='services',
        help_text="Department this service belongs to"
    )
    name = models.CharField(max_length=255, help_text="Service name (e.g., Khám tổng quát)")
    description = models.TextField(blank=True, null=True, help_text="Service description")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Service price in VND")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['department', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"

class Room(models.Model):
    """
    Room model - Appointment rooms
    """
    room_number = models.CharField(max_length=50, unique=True, help_text="Room number (e.g., P101)")
    floor = models.IntegerField(blank=True, null=True, help_text="Floor number")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rooms',
        help_text="Department/area this room belongs to"
    )    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rooms'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['floor', 'room_number']
    
    def __str__(self):
        return f"Room {self.room_number}"


class Appointment(models.Model):
    """
    Appointment model - Patient appointments
    """
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Tạo TIME_CHOICES với khoảng cách 30 phút (08:00 - 16:30)
    TIME_CHOICES = [
        ('08:00:00', '08:00'),
        ('08:30:00', '08:30'),
        ('09:00:00', '09:00'),
        ('09:30:00', '09:30'),
        ('10:00:00', '10:00'),
        ('10:30:00', '10:30'),
        ('11:00:00', '11:00'),
        ('11:30:00', '11:30'),
        ('12:00:00', '12:00'),
        ('12:30:00', '12:30'),
        ('13:00:00', '13:00'),
        ('13:30:00', '13:30'),
        ('14:00:00', '14:00'),
        ('14:30:00', '14:30'),
        ('15:00:00', '15:00'),
        ('15:30:00', '15:30'),
        ('16:00:00', '16:00'),
        ('16:30:00', '16:30'),
    ]
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        limit_choices_to={'role': 'patient'},
        help_text="Patient who booked the appointment"
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'doctor'},
        help_text="Doctor assigned to the appointment"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT, #không cho xoá dept nếu có appointments
        related_name='appointments',
        help_text="Department/specialty that patient selected (e.g., 'Nhi khoa', 'Tim mạch')",
    )
    # Service sẽ được doctor assign sau khi khám
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,  
        null=True,                 
        blank=True,                 
        related_name='appointments',
        help_text="Service assigned by doctor after consultation (optional when booking)"
    )
    appointment_date = models.DateField(help_text="Date of appointment")
    appointment_time = models.TimeField(
        help_text="Time of appointment",
        choices=TIME_CHOICES
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        help_text="Room assigned for the appointment"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming',
        help_text="Current status of the appointment"
    )
    symptoms = models.TextField(blank=True, null=True, help_text="Patient symptoms description")
    reason = models.TextField(blank=True, null=True, help_text="Reason for appointment")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    estimated_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Estimated consultation fee"
    )
    cancellation_reason = models.TextField(blank=True, null=True, help_text="Reason for cancellation")
    cancelled_at = models.DateTimeField(blank=True, null=True, help_text="When appointment was cancelled")
    rescheduled_from = models.JSONField(
        blank=True,
        null=True,
        help_text="Previous appointment date/time if rescheduled (format: {'date': 'YYYY-MM-DD', 'time': 'HH:MM'})"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['doctor', 'appointment_date']),
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"Appointment #{self.id} - {self.patient.full_name} with Dr. {self.doctor.full_name} on {self.appointment_date} at {self.appointment_time}"


class MedicalRecord(models.Model):
    """
    Medical Record model - Doctor's medical record for an appointment
    One-to-one relationship with Appointment
    """
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='medical_record',
        help_text="Appointment this medical record belongs to"
    )
    diagnosis = models.TextField(
        blank=True,
        null=True,
        help_text="Doctor's diagnosis"
    )
    prescription = models.TextField(
        blank=True,
        null=True,
        help_text="Prescription details (medications, dosage, instructions)"
    )
    treatment_plan = models.TextField(
        blank=True,
        null=True,
        help_text="Treatment plan and recommendations"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional medical notes"
    )
    follow_up_date = models.DateField(
        blank=True,
        null=True,
        help_text="Recommended follow-up date if needed"
    )
    vital_signs = models.JSONField(
        blank=True,
        null=True,
        help_text="Vital signs (blood pressure, temperature, heart rate, etc.) in JSON format"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_medical_records',
        limit_choices_to={'role': 'doctor'},
        help_text="Doctor who created this medical record"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['appointment']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"Medical Record for Appointment #{self.appointment.id} - {self.appointment.patient.full_name}"
