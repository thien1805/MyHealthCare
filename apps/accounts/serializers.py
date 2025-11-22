from rest_framework import serializers
from django.contrib.auth import get_user_model #import custom user model
from .models import Patient, Doctor
from django.core.validators import RegexValidator
import logging

logger = logging.getLogger(__name__)
User = get_user_model()
#Serializer in DRF dùng để chuyển đổi dữ liệu từ Python object/Query set => Json
#Serialization: Chuyển dữ liệu từ model -> JSON -> gửi ra ngoài cho client (React, Postman)
#Deserialization: Nhận Json từ request -> kiểm tra, validate -> Chuyển thành Python objet hoặc moddel instance để lưu vào DB


#Serializer for Register - create a new patient
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer to register a new user"""
    """
    - Nhận data từ frontend để tạo user mới
    - Validate data
    - Tạo User và Patient profile
    """
    
    #Step1. Declare extra fielđs
    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(required=True)
    #Field password (not in User model)
    password = serializers.CharField(write_only=True, min_length=6) #just write, not response.
    password_confirm = serializers.CharField(write_only=True)
    phone_num = serializers.CharField(
        validators=[RegexValidator(r'^\d{10}$', 'Phone number must be exactly 10 digits.')]
    )
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=Patient.GENDER_CHOICES, required=True)
    address = serializers.CharField(required=True, allow_blank=True)
    
    #Step2. Meta class - Serializater config
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'full_name', 'phone_num', 'role',
                  'date_of_birth', 'gender', 'address'
                  ]
        
    #Step 3. Validate methods
    def validate(self, attrs):
        """
        Custom validation:
        - Django DRF sẽ tự động validate các field theo kiểu dữ liệu đã khai báo
        - data = dictionary chứa tất cả data đã được validate theo fields
        """
    
        #Check 1: password match
        pwd1 = attrs.get('password')
        pwd2 = attrs.get('password_confirm')
        if pwd1 != pwd2:
            raise serializers.ValidationError({
                "password_confirm": "Password do not match"
            })
        #Check 2: Role must be 'patient' for registering
        if attrs.get('role') != 'patient':
            raise serializers.ValidationError({
                "role": "Role must be 'patient' for registering"
            })
        #If passing all validation -> return data
        return attrs
    
    #Step 4: Create method - create records:
    def create(self, validated_data):
        """
        Create a new user and patient profile (if needed)
        - validated_data = data is already validated()
        - Django DRF will be automatically called when we use serializer.save()
        """
        try:
            #Step 4.1: Extract and remove the fields not in User model
            validated_data.pop('password_confirm') #remove password_confirm from dict
            
            #Step 4.2: Extract email, password, and full_name BEFORE creating user (QUAN TRỌNG!)
            email = validated_data.pop('email')
            password = validated_data.pop('password')
            full_name = validated_data.pop('full_name')
            
            #Step 4.3: Extract Patient fields
            date_of_birth = validated_data.pop('date_of_birth', None)
            gender = validated_data.pop('gender', None)
            address = validated_data.pop('address', None)
            
            #Step 4.4: Create User with email, password, and full_name as separate parameters
            user = User.objects.create_user(email=email, password=password, full_name=full_name, **validated_data)
            
            #Step 4.5: If role = patient -> Create patient profile
            if user.role == 'patient':
                Patient.objects.create(
                    user=user,
                    date_of_birth=date_of_birth,
                    gender=gender, 
                    address=address
                )
            return user
        except Exception as e:
            # Log error for debugging
            logger.error(f"Error in RegisterSerializer.create: {str(e)}", exc_info=True)
            # Re-raise to let transaction rollback
            raise
    
class LoginSerializer(serializers.Serializer):
    """Serializer for user login
    - CHÚ Ý: Inherit từ Serializer (không phải ModelSerializer)
    - Vì không tạo/update model, chỉ validate input
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    

# Serializer for Patient Profile
class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for Patient profile information"""
    emergency_contact_phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[RegexValidator(r'^\d{10}$', 'Emergency contact phone must be exactly 10 digits.')],
        help_text="Emergency contact phone number (exactly 10 digits)"
    )
    
    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 
            'gender', 
            'address', 
            'insurance_id', 
            'emergency_contact', 
            'emergency_contact_phone'
        ]
        read_only_fields = []
    
    def validate_emergency_contact_phone(self, value):
        """Validate emergency contact phone number"""
        if value:
            if not value.isdigit() or len(value) != 10:
                raise serializers.ValidationError("Emergency contact phone must be exactly 10 digits.")
        return value

class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for Doctor profile information"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.IntegerField(source='department.id', read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'department_id',
            'department_name',
            'title', 
            'specialization', 
            'license_number', 
            'experience_years', 
            'consultation_fee', 
            'bio'
        ] 
        read_only_fields = ['license_number', 'department_id', 'department_name']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User profile information"""
    patient_profile = PatientProfileSerializer(read_only=True, required=False)
    doctor_profile = DoctorProfileSerializer(read_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_num', 'role', 'is_active', 'created_at', 'updated_at', 'patient_profile', 'doctor_profile']
        read_only_fields = ['id','email', 'role', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Custom representation để chỉ trả về profile tương ứng với role"""
        data = super().to_representation(instance)
        
        # Chỉ giữ profile tương ứng với role của user
        # XÓA profile không phù hợp để đảm bảo không hiển thị
        if instance.role == 'patient':
            # Patient: chỉ có patient_profile
            try:
                if hasattr(instance, 'patient_profile') and instance.patient_profile:
                    data['patient_profile'] = PatientProfileSerializer(instance.patient_profile).data
                else:
                    data['patient_profile'] = None
            except:
                data['patient_profile'] = None
            # XÓA doctor_profile - không bao giờ hiển thị cho patient
            data.pop('doctor_profile', None)
            
        elif instance.role == 'doctor':
            # Doctor: chỉ có doctor_profile
            try:
                if hasattr(instance, 'doctor_profile') and instance.doctor_profile:
                    data['doctor_profile'] = DoctorProfileSerializer(instance.doctor_profile).data
                else:
                    data['doctor_profile'] = None
            except:
                data['doctor_profile'] = None
            # XÓA patient_profile - không bao giờ hiển thị cho doctor
            data.pop('patient_profile', None)
            
        else:
            # Admin hoặc role khác: không có profile
            data.pop('patient_profile', None)
            data.pop('doctor_profile', None)
            
        return data
        
class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating User profile information"""
    # Không khai báo cả 2 profiles ở đây, sẽ dùng to_representation để chỉ hiển thị đúng profile
    class Meta:
        model = User
        #Chỉ cho phép update những fields này
        fields = ['full_name', 'phone_num']
        #Chỉ cho phép đọc những fields này
        read_only_fields = ['id','email', 'role', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        """Dynamic fields based on user role"""
        super().__init__(*args, **kwargs) #khởi tạo serializer với các fields đã khai báo trong Meta class
        
        # Lấy instance từ args hoặc kwargs
        # Instance có thể ở vị trí đầu tiên trong args nếu được truyền như: Serializer(instance)
        instance = kwargs.get('instance') or (args[0] if args and hasattr(args[0], 'role') else None)
        # Lấy partial từ kwargs (True cho PATCH, False cho PUT)
        # Luôn set partial=True cho nested serializer để cho phép update một phần
        partial = kwargs.get('partial', True)  # Mặc định True để cho phép update một phần
        
        if instance and hasattr(instance, 'role'):
            # Chỉ thêm profile field đúng với role
            if instance.role == 'patient':
                # Set partial=True cho nested serializer để cho phép update một phần
                # Cho phép update các fields như emergency_contact, emergency_contact_phone, insurance_id, etc.
                self.fields['patient_profile'] = PatientProfileSerializer(required=False, partial=True)
            elif instance.role == 'doctor':
                # Set partial=True cho nested serializer để cho phép update một phần
                # Cho phép update các fields như title, specialization, consultation_fee, bio, etc.
                self.fields['doctor_profile'] = DoctorProfileSerializer(required=False, partial=True)
            # Admin hoặc role khác: không có profile fields
    
    def to_representation(self, instance):
        """Custom representation để hiển thị nested profile trong form HTML"""
        data = super().to_representation(instance)
        
        # Thêm nested profile data để form HTML có thể hiển thị
        if instance.role == 'patient':
            try:
                if hasattr(instance, 'patient_profile') and instance.patient_profile:
                    data['patient_profile'] = PatientProfileSerializer(instance.patient_profile).data
                else:
                    data['patient_profile'] = None
            except:
                data['patient_profile'] = None
        elif instance.role == 'doctor':
            try:
                if hasattr(instance, 'doctor_profile') and instance.doctor_profile:
                    data['doctor_profile'] = DoctorProfileSerializer(instance.doctor_profile).data
                else:
                    data['doctor_profile'] = None
            except:
                data['doctor_profile'] = None
        
        return data
    
    def validate_phone_num(self, value):
        """
        Custom validation cho phone_num field
        DRF tự động gọi method validate_<field_name> khi validate field đó
        """
        if value and not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value
    
    def update(self, instance, validated_data):
        """
        Customer update logic để xử lí nested profile
        instance: user object hiện tại
        validated_data: dict chứa data đã được validate
        """
        
        #Tách nested profile data ra khỏi validated_data 
        #pop: lấy value và xoá key khỏi dict
        #pop('patient_profile', None): lấy patient_profile, nếu không có trả về None
        patient_profile_data = validated_data.pop('patient_profile', None)
        doctor_profile_data = validated_data.pop('doctor_profile', None)
        
        #Update các field của User (full_name, phone_num)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        #Update Patient Profile if exists and data provided
        if instance.role == "patient" and patient_profile_data is not None:
            patient_profile, created = Patient.objects.get_or_create(user=instance)
            # Update từng field trong patient_profile_data
            # Sử dụng nested serializer để update đúng cách
            patient_serializer = PatientProfileSerializer(
                instance=patient_profile, 
                data=patient_profile_data, 
                partial=True
            )
            if patient_serializer.is_valid():
                patient_serializer.save()
            else:
                # Nếu validation fail, fallback về cách cũ
                for attr, value in patient_profile_data.items():
                    # Cho phép set None hoặc empty string cho các fields optional
                    setattr(patient_profile, attr, value)
                patient_profile.save()
        
        elif instance.role == "doctor" and doctor_profile_data is not None:
            doctor_profile, created = Doctor.objects.get_or_create(user=instance)
            # Sử dụng nested serializer để update đúng cách
            doctor_serializer = DoctorProfileSerializer(
                instance=doctor_profile,
                data=doctor_profile_data,
                partial=True
            )
            if doctor_serializer.is_valid():
                doctor_serializer.save()
            else:
                # Nếu validation fail, fallback về cách cũ
                for attr, value in doctor_profile_data.items():
                    setattr(doctor_profile, attr, value)
                doctor_profile.save()
        
        return instance