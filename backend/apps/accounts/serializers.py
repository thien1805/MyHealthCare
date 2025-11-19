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

class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for Doctor profile information"""
    class Meta:
        model = Doctor
        fields = [
            'title', 
            'specialization', 
            'license_number', 
            'experience_years', 'consultation_fee', 'bio'
        ] 
        read_only_fields = ['license_number']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User profile information"""
    patient_profile = PatientProfileSerializer(read_only=True, required=False)
    doctor_profile = DoctorProfileSerializer(read_only=True, required=False)
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_num', 'role', 'is_active', 'created_at', 'updated_at', 'patient_profile', 'doctor_profile']
        read_only_fields = ['id','email', 'role', 'created_at', 'updated_at']
        
class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating User profile information"""
    #required=False: không bắt buộc phải có field này trong request
    patient_profile = PatientProfileSerializer(required=False)
    doctor_profile = DoctorProfileSerializer(required=False)
    class Meta:
        model = User
        #Chỉ cho phép update những fields này
        fields = ['full_name', 'phone_num', 'patient_profile', 'doctor_profile']
        #Chỉ cho phép đọc những fields này
        read_only_fields = ['id','email', 'role', 'created_at', 'updated_at']
    
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
            for attr, value in patient_profile_data.items():
                setattr(patient_profile, attr, value)
            patient_profile.save()
        
        elif instance.role == "doctor" and doctor_profile_data is not None:
            doctor_profile, created = Doctor.objects.get_or_create(user=instance)
            for attr, value in doctor_profile_data.items():
                setattr(doctor_profile, attr, value)
            doctor_profile.save()
        
        return instance