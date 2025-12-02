from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Service, Room, Appointment, Department, MedicalRecord
from apps.accounts.models import Doctor

User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model
    """
    services_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'icon',
            'description',
            'health_examination_fee',
            'is_active',
            'services_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_services_count(self, obj):
        """Return count of active services in this department"""
        return obj.services.filter(is_active=True).count()
    def get_doctor_count(self, obj): 
        from apps.accounts.models import Doctor
        return Doctor.objects.filter(department=obj, 
        user__is_active=True).count()
    
class DepartmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model with detailed information
    Includes services and doctors
    """
    services = serializers.SerializerMethodField()
    doctors = serializers.SerializerMethodField()
    services_count = serializers.SerializerMethodField()
    doctors_count = serializers.SerializerMethodField()
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'icon',
            'description',
            'health_examination_fee',
            'is_active',
            'services',
            'doctors',
            'services_count',
            'doctors_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_services(self, obj):
        """
        Return list of active services in this department
        Ordered by name
        """
        services = obj.services.filter(is_active=True).order_by('name')
        return [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "price": service.price,
                "is_active": service.is_active,
            }
            for service in services
        ]
    
    def get_doctors(self, obj):
        """
        Return list of active doctors in this department
        Ordered by rating and full_name
        """
        from apps.accounts.models import Doctor
        doctors = Doctor.objects.filter(
            department=obj,
            user__is_active=True
        ).select_related('user', 'department').order_by('-rating', 'user__full_name')
        
        return [
            {
                "id": doctor.id,
                "full_name": doctor.user.full_name,
                "email": doctor.user.email,
                "phone_num": doctor.user.phone_num,
                "title": doctor.title,
                "specialization": doctor.specialization,
                "department_id": doctor.department.id,
                "department_name": doctor.department.name,
                "department_icon": doctor.department.icon,
                "experience_years": doctor.experience_years,
                "consultation_fee": str(doctor.consultation_fee),
                "rating": float(doctor.rating),
                "avatar_url": doctor.avatar_url,  # avatar_url là field của Doctor, không phải User
                "total_reviews": doctor.total_reviews,
                "bio": doctor.bio
            }
            for doctor in doctors
        ]
    def get_services_count(self, obj):
        """Return count of active services in this department"""
        return obj.services.filter(is_active=True).count()
    def get_doctors_count(self, obj):
        """Return count of active doctors in this department"""
        from apps.accounts.models import Doctor
        return Doctor.objects.filter(
            department=obj,
            user__is_active=True
        ).count()
    
class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service model
    Used for listing services/specialties
    """
    department_id = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    department_icon = serializers.SerializerMethodField()
    
    def get_department_id(self, obj):
        return obj.department.id if obj.department else None

    def get_department_name(self, obj):
        """Return department name"""
        return obj.department.name if obj.department else None
    
    def get_department_icon(self, obj):
        """Return department icon"""
        return obj.department.icon if obj.department else None
    
    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'department_id',
            'department_name',
            'department_icon',
            'description',
            'price',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'department_name', 'department_icon', 'department_id']


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for Room model
    Used for room information in appointments
    """
    class Meta:
        model = Room
        fields = [
            'id',
            'room_number',
            'floor',
            'department',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DoctorListSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor listing in booking UI
    Includes user info, rating, experience, fee, department
    """
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_num = serializers.CharField(source='user.phone_num', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.IntegerField(source='department.id', read_only=True)
    department_icon = serializers.CharField(source='department.icon', read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id',
            'full_name',
            'email',
            'phone_num',
            'title',
            'specialization',
            'department_id',
            'department_name',
            'department_icon',
            'experience_years',
            'consultation_fee',
            'rating',
            'avatar_url',
            'total_reviews',
            'bio'
        ]
        read_only_fields = ['id', 'license_number']


class AvailableSlotSerializer(serializers.Serializer):
    """
    Serializer for available time slots response
    Not a ModelSerializer because it's calculated data
    """
    time = serializers.TimeField(help_text="Time slot (e.g., 09:00)")
    available = serializers.BooleanField(help_text="Whether this slot is available")
    room = serializers.CharField(help_text="Room number if available", required=False, allow_null=True)


class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for Medical Record model
    """
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id',
            'appointment',
            'diagnosis',
            'prescription',
            'treatment_plan',
            'notes',
            'follow_up_date',
            'vital_signs',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'appointment',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
    
    def validate_vital_signs(self, value):
        """Validate vital signs JSON structure"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Vital signs must be a JSON object")
        return value


class MedicalRecordCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating Medical Record
    Used by doctor to create or update medical record
    """
    class Meta:
        model = MedicalRecord
        fields = [
            'diagnosis',
            'prescription',
            'treatment_plan',
            'notes',
            'follow_up_date',
            'vital_signs',
        ]
    
    def validate_vital_signs(self, value):
        """Validate vital signs JSON structure"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Vital signs must be a JSON object")
        return value


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment model
    Used for CRUD operations on appointments
    """
    # Nested serializers for related objects
    patient = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    service = ServiceSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    medical_record = MedicalRecordSerializer(read_only=True, required=False)
    
    # Write-only fields for creating/updating
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='patient'),
        write_only=True,
        required=False,
        source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='doctor'),
        write_only=True,
        source='doctor'
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True),
        write_only=True,
        source='service'
    )
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True),
        write_only=True,
        required=False,
        allow_null=True,
        source='room'
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        write_only=True,
        required=False,
        source='department'
    )
    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'patient_id',
            'doctor',
            'doctor_id',
            'department',
            'department_id',
            'service',
            'service_id',
            'appointment_date',
            'appointment_time',
            'room',
            'room_id',
            'status',
            'symptoms',
            'reason',
            'notes',
            'estimated_fee',
            'cancellation_reason',
            'cancelled_at',
            'rescheduled_from',
            'medical_record',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'patient',
            'doctor',
            'service',
            'room',
            'status',
            'estimated_fee',
            'cancellation_reason',
            'cancelled_at',
            'rescheduled_from',
            'created_at',
            'updated_at'
        ]
    
   

    def get_patient(self, obj):
        """Return simplified patient info"""
        return {
            'id': obj.patient.id,
            'full_name': obj.patient.full_name,
            'email': obj.patient.email
        }
    
    def get_doctor(self, obj):
        """Return doctor info with profile"""
        doctor_profile = obj.doctor.doctor_profile
        return {
            'id': obj.doctor.id,
            'full_name': obj.doctor.full_name,
            'specialization': doctor_profile.specialization,
            'title': doctor_profile.title,
            'rating': float(doctor_profile.rating),
            'avatar_url': doctor_profile.avatar_url
        }
    
    def validate_appointment_date(self, value):
        """Validate appointment date is in the future"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if value < today:
            raise serializers.ValidationError("Appointment date must be in the future.")
        
        # Max 30 days in advance
        max_date = today + timezone.timedelta(days=30)
        if value > max_date:
            raise serializers.ValidationError("Cannot book appointments more than 30 days in advance.")
        
        return value
    
    def validate_appointment_time(self, value):
        """Validate appointment time is within working hours"""
        from datetime import time
        
        # Working hours: 08:00 - 16:30
        start_time = time(8, 0)
        end_time = time(16, 30)
        
        if value < start_time or value > end_time:
            raise serializers.ValidationError("Appointment time must be between 08:00 and 16:30.")
        
        # Check if time is in 30-minute intervals
        if value.minute not in [0, 30]:
            raise serializers.ValidationError("Appointment time must be in 30-minute intervals (e.g., 09:00, 09:30).")
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Check if doctor and service are active
        doctor = attrs.get('doctor')
        if doctor and not doctor.is_active:
            raise serializers.ValidationError({
                'doctor_id': 'Selected doctor is not active.'
            })
        
        service = attrs.get('service')
        if service and not service.is_active:
            raise serializers.ValidationError({
                'service_id': 'Selected service is not active.'
            })
        
        return attrs


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating appointments
    Used in POST /api/v1/appointments/
    Room will be automatically assigned from doctor's room
    """
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='doctor', is_active=True),
        source='doctor',
        help_text="Doctor ID"
    )
    # XÓA room_id field - Room sẽ được tự động gán từ doctor.room
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        source='department',
        help_text="Department ID",
        required=True
    )

    class Meta:
        model = Appointment
        fields = [
            'doctor_id',
            'department_id',
            'appointment_date',
            'appointment_time',
            # 'room_id',  # XÓA - Room sẽ tự động gán
            'symptoms',
            'reason',
            'notes'
        ]
    
    def validate(self, attrs):
        """Cross-field validation"""
        doctor = attrs.get('doctor')
        department = attrs.get('department')
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')
        
        if doctor and not doctor.is_active:
            raise serializers.ValidationError({
                'doctor_id': 'Selected doctor is not active.'
            })
        if department and not department.is_active:
            raise serializers.ValidationError({
                'department_id': 'Selected department is not active.'
            })
        
        # Kiểm tra doctor có thuộc department không
        if doctor and department:
            try:
                doctor_profile = doctor.doctor_profile
                if doctor_profile.department != department:
                    raise serializers.ValidationError({
                        'doctor_id': f'Doctor does not belong to department "{department.name}". Doctor belongs to "{doctor_profile.department.name}".'
                    })
            except AttributeError:
                raise serializers.ValidationError({
                    'doctor_id': 'Doctor profile not found.'
                })
        
        # Check if time slot is available
        if doctor and appointment_date and appointment_time:
            conflicting_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['booked', 'confirmed']
            ).exists()
            
            if conflicting_appointment:
                raise serializers.ValidationError({
                    'appointment_time': 'This time slot is already taken. Please choose another time.'
                })
        
        return attrs
    def validate_appointment_date(self, value):
        """Validate appointment date is in the future"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if value < today:
            raise serializers.ValidationError("Appointment date must be in the future.")
        
        # Max 30 days in advance
        max_date = today + timezone.timedelta(days=30)
        if value > max_date:
            raise serializers.ValidationError("Cannot book appointments more than 30 days in advance.")
        
        return value
    
    def validate_appointment_time(self, value):
        """Validate appointment time is within working hours"""
        from datetime import time, datetime
        
        # Convert string to time object if needed (from HTML form)
        if isinstance(value, str):
            try:
                # Try parsing time string (e.g., "09:00", "09:00:00")
                if len(value) == 5:  # Format: "HH:MM"
                    hour, minute = map(int, value.split(':'))
                    value = time(hour, minute)
                elif len(value) >= 8:  # Format: "HH:MM:SS" or longer
                    time_obj = datetime.strptime(value.split('.')[0], '%H:%M:%S').time()
                    value = time_obj
                else:
                    raise serializers.ValidationError("Invalid time format. Use HH:MM format (e.g., 09:00).")
            except (ValueError, AttributeError) as e:
                raise serializers.ValidationError(f"Invalid time format: {value}. Use HH:MM format (e.g., 09:00).")
        
        # Ensure value is a time object
        if not isinstance(value, time):
            raise serializers.ValidationError(f"Invalid time value: {value}. Must be a time object.")
        
        # Working hours: 08:00 - 16:30
        start_time = time(8, 0)
        end_time = time(16, 30)
        
        if value < start_time or value > end_time:
            raise serializers.ValidationError("Appointment time must be between 08:00 and 16:30.")
        
        # Check if time is in 30-minute intervals
        if value.minute not in [0, 30]:
            raise serializers.ValidationError("Appointment time must be in 30-minute intervals (e.g., 09:00, 09:30).")
        
        return value



class AppointmentRescheduleSerializer(serializers.Serializer):
    """
    Serializer for rescheduling appointments
    Used in PUT /api/v1/appointments/{id}/reschedule/
    """
    new_date = serializers.DateField(required=True)
    new_time = serializers.TimeField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_new_date(self, value):
        """Validate new date is in the future"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if value < today:
            raise serializers.ValidationError("New appointment date must be in the future.")
        
        # Max 30 days in advance
        max_date = today + timezone.timedelta(days=30)
        if value > max_date:
            raise serializers.ValidationError("Cannot reschedule appointments more than 30 days in advance.")
        
        return value
    
    def validate_new_time(self, value):
        """Validate new time is within working hours"""
        from datetime import time
        
        # Working hours: 08:00 - 16:30
        start_time = time(8, 0)
        end_time = time(16, 30)
        
        if value < start_time or value > end_time:
            raise serializers.ValidationError("Appointment time must be between 08:00 and 16:30.")
        
        # Check if time is in 30-minute intervals
        if value.minute not in [0, 30]:
            raise serializers.ValidationError("Appointment time must be in 30-minute intervals (e.g., 09:00, 09:30).")
        
        return value


class AppointmentCancelSerializer(serializers.Serializer):
    """
    Serializer for cancelling appointments
    Used in POST /api/v1/appointments/{id}/cancel/
    """
    reason = serializers.CharField(required=False, allow_blank=True, help_text="Reason for cancellation")


class AppointmentAssignServiceSerializer(serializers.Serializer):
    """
    Serializer for assigning service to appointment
    Used in POST /api/v1/appointments/{id}/assign-service/
    """
    service_id = serializers.IntegerField(required=True, help_text="Service ID to assign to the appointment") 

