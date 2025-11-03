from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Manage để tạo user với email thay vì username
    """
    def create_user(self, email, password=None, **extra_fields):
        """Tạo user thường"""
        if not email: 
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Tạo admin user"""
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role of Admin')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        return self.create_user(email, password, **extra_fields)

        
class User(AbstractBaseUser, PermissionsMixin):
    """
    Bảng User - lưu thông tin người dùng chung
    """                   
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_num = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    #Connect to UserManager
    objects = UserManager()
    
    #Login by email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User' #số ít
        verbose_name_plural = 'Users' #số nhiều
        
    def __str__(self):
        return f"{self.full_name} ({self.role})"
        

