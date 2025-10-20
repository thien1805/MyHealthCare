from rest_framework import serializers
from django.contrib.auth import get_user_model #import custom user model
from .models import Patient, Doctor

User = get_user_model()

#Serializer for User
class UserSerializer(serializers.ModelSerializer):
    """Display the User information"""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_num', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at']
        
#Serializer for Register - create a new patient
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer to register a new user"""
    """
    - Nhận data từ frontend để tạo user mới
    - Validate data
    - Tạo User và Patient profile
    """
    
    #Step1. Declare extra fielđs
    
    #Field password (not in User model)
    password = serializers.CharField(write_only=True, min_length=6) #just write, not response.
    password_confirm = serializers.CharField(write_only=True)
    
    #Patient fields: (optional)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=Patient.GENDER_CHOICES, required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True)
    
    #Step2. Meta class - Serializater config
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'full_name', 'phone_num', 'role'
                  #Patient fields (extra)
                  'date_of_birth', 'gender', 'address'
                  ]
        
    #Step 3. Validate methods
    def validate(self, data):
        """
        Custom validation:
        - Django DRF sẽ tự động validate các field theo kiểu dữ liệu đã khai báo
        - data = dictionary chứa tất cả data đã được validate theo fields
        """
    
    #Check 1: password match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password": "password confirm does not match"
            })
    #Check 2: Role must be 'patient' for registering
        if data.get['role'] not in ['patient', 'doctor', 'admin']:
            raise serializers.ValidationError({
                "role": "Role is not valid"
            })
    #If passing all validation -> return data
        return data
    
    #Step 4: Create method - create records:
    def create(self, validated_data):
        """
        Create a new user and patient profile (if needed)
        - validated_data = data is already validated()
        - Django DRF will be automatically called when we use serializer.save()
        """
        
        #Step 4.1: Extract and remove the fields not in User model
        validated_data.pop('password_confirm') #remove password_confirm from dict
        
        date_of_birth = validated_data.pop('date_of_birth', None)
        gender = validated_data.pop('gender', None)
        address = validated_data.pop('address', None)
        
        #Step 4.2: Create User
        user = User.objects.create_user(**validated_data)
        
        #Step 4.3: If role = patient -> Create patient profile
        if user.role == 'patient':
            Patient.objects.create(
                user=user,
                date_of_birth=date_of_birth,
                gender=gender, 
                address=address
            )
        return user
    
class LoginSerializer(serializers.Serializer):
    """Serializer for user login
    - CHÚ Ý: Inherit từ Serializer (không phải ModelSerializer)
    - Vì không tạo/update model, chỉ validate input
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    