from rest_framework import status, generics

from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError as DRFValidationError
from .models import User, Doctor
from .serializers import RegisterSerializer, RegisterResponseSerializer, UserSerializer, LoginSerializer, ProfileUpdateSerializer, DoctorProfileSerializer, PatientProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.conf import settings
from django.apps import apps
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import logging
from .serializers import ForgotPasswordSerializer, VerifyResetTokenSerializer, ResetPasswordSerializer

logger = logging.getLogger(__name__)

# Check if token_blacklist app is installed
BLACKLIST_ENABLED = apps.is_installed('rest_framework_simplejwt.token_blacklist')
#Registration API 

User = get_user_model()
class RegisterView(generics.CreateAPIView):
    """
    API to register a new patient
    POST /api/v1/auth/register/
    """
    query_set = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] #anyone can access this API
    
    @extend_schema(
        operation_id="auth_register",
        summary="Register new patient",
        description="Register a new patient account. Creates both User and Patient profile.",
        tags=["Authentication"],
        request=RegisterSerializer,
        responses={
            201: {
                'description': 'User registered successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'User registered successfully',
                            'user': {
                                'id': 1,
                                'email': 'patient@example.com',
                                'full_name': 'John Doe',
                                'phone_num': '0123456789',
                                'role': 'patient',
                                'is_active': True,
                                'created_at': '2024-01-01T00:00:00Z',
                                'updated_at': '2024-01-01T00:00:00Z',
                                'patient_profile': {
                                    'date_of_birth': '1990-01-01',
                                    'gender': 'male',
                                    'address': '123 Main St'
                                }
                            },
                            'tokens': {
                                'refresh': 'refresh_token_string',
                                'access': 'access_token_string'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Validation error',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'message': 'An error occurred while registering. Please try again.',
                            'error': 'Validation error details'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Register Example',
                value={
                    'email': 'patient@example.com',
                    'password': 'password123',
                    'password_confirm': 'password123',
                    'full_name': 'John Doe',
                    'phone_num': '0123456789',
                    'role': 'patient',
                    'date_of_birth': '1990-01-01',
                    'gender': 'male',
                    'address': '123 Main St'
                },
                request_only=True,
            )
        ]
    )
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new user with transaction rollback if any error occurs
        """
        try:
            #validate input
            serializer = self.get_serializer(data=request.data) #initial_data (raw data from request)
            serializer.is_valid(raise_exception=True) #call validate method, if not valid, raise exception
            
            #create user and patient profile (inside transaction)
            user = serializer.save() #call create method in register serializer
            
            #create the JWT token for the new user
            refresh = RefreshToken.for_user(user)
            
            #serialize user data - refresh from DB to get updated_at
            user.refresh_from_db()
            user_data = UserSerializer(user).data
            
            #return success response
            return Response({
                "success": True,
                "message": "User registered successfully",
                "user": user_data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token) #access token
                }
            }, status=status.HTTP_201_CREATED)
            
        except DRFValidationError:
            # Let DRF handle ValidationError (will return 400 Bad Request)
            # Transaction will be automatically rolled back due to @transaction.atomic
            raise
            
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error in RegisterView.create: {str(e)}", exc_info=True)
            
            # Transaction will be automatically rolled back due to @transaction.atomic
            # Return error response
            return Response({
                "success": False,
                "message": "An error occurred while registering. Please try again.",
                "error": str(e) if settings.DEBUG else "Sorry, something went wrong. Please try again later."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
#Login API
class LoginView(generics.GenericAPIView):
    """
    API login user
    Return access and refresh token for authentication
    POST /api/v1/auth/login/
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id="auth_login",
        summary="Login",
        description="Login with email and password",
        tags=["Authentication"],
        request=LoginSerializer,
        responses={
            200: {
                'description': 'Login successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Login successfully',
                            'user': {
                                'id': 1,
                                'email': 'test@example.com',
                                'full_name': 'John Doe'
                            },
                            'tokens': {
                                'refresh': 'refresh_token',
                                'access': 'access_token'
                            }
                        }
                    }
                }
            },
            401: {
                'description': 'Invalid email or password',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'message': 'Invalid email or password'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Login Example',
                value={
                    'email': 'patient@example.com',
                    'password': 'password123'
                },
                request_only=True,
            )
        ]
    )
    
    
    def post(self, request):
        #Step1: Validate input data
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        #Step 2: Authenticate user
        # Hàm này sẽ tự động hash password nhập vào và so sánh với DB
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({
                "success": False,
                "message": "Invalid email or password"
            }, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({
                "success": False,
                "message": "User account is disabled"
            }, status=status.HTTP_403_FORBIDDEN)
        
        #Tạo Django session
        login(request, user)
        #Step 3: Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "success": True,
            "message": "Login successfully",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        })

class LogoutView(APIView):
    """
    Logout from current device
    POST /api/v1/auth/logout/
    Blacklist refresh token
    """
    #Chỉ cho phép user đã đăng nhập mới gọi API này
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="auth_logout",
        summary="Logout from current device",
        description="Logout from current device and blacklist the refresh token. Requires authentication.",
        tags=["Authentication"],
        request={
            'type': 'object',
            'properties': {
                'refresh': {
                    'type': 'string',
                    'description': 'Refresh token to blacklist'
                },
                'redirect_url': {
                    'type': 'string',
                    'description': 'Optional redirect URL after logout',
                    'default': '/api/v1/auth/login'
                }
            },
            'required': ['refresh']
        },
        responses={
            200: {
                'description': 'Logout successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Logout successfully',
                            'redirect_url': '/api/v1/auth/login'
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request - missing refresh token or invalid token',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'message': 'Refresh token is required'
                        }
                    }
                }
            },
            401: {
                'description': 'Unauthorized - authentication required'
            }
        },
        examples=[
            OpenApiExample(
                'Logout Example',
                value={
                    'refresh': 'refresh_token_string',
                    'redirect_url': '/api/v1/auth/login'
                },
                request_only=True,
            )
        ]
    )
    def post(self, request):
        try:
            #Lấy refresh token từ request body 
            refresh_token = request.data.get("refresh")
            
            if not refresh_token:
                return Response({
                    "success": False, 
                    "message": "Refresh token is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            #Tạo đối tượng RefreshToken từ chuỗi token nhận được, sẽ tự động decode và verify token có hơp le
            token = RefreshToken(refresh_token)

            # Kiểm tra xem 'rest_framework_simplejwt.token_blacklist' có được cài đặt không
            if 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS:
                token.blacklist()
            
            logout(request)
            
            redirect_url = request.data.get('redirect_url', '/api/v1/auth/login')

            return Response({
                "success": True,
                "message": "Logout successfully",
                "redirect_url": redirect_url
            }, status=status.HTTP_200_OK)

        #Xử lí lỗi khi token không hợp lệ (đã hết hạn, sai format)
        except TokenError:
            return Response({
                "success": False,
                "message": "Token is invalid or expired"
            }, status=status.HTTP_400_BAD_REQUEST)
        #Xử lí lỗi ngoại lệ khác
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutAllView(APIView):
    """Logout khỏi tất cả thiết bị
    POST /api/v1/auth/logout-all/
    Blacklist tất cả token của user
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        operation_id="auth_logout_all",
        summary="Logout from all devices",
        description="Logout from all devices and blacklist all refresh tokens for the current user. Requires authentication.",
        tags=["Authentication"],
        responses={
            205: {
                'description': 'Logged out from all devices successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Logged out from all devices successfully'
                        }
                    }
                }
            },
            401: {
                'description': 'Unauthorized - authentication required'
            },
            500: {
                'description': 'Internal server error',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'message': 'Error message'
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        try:
            #Lấy tất cả token của user còn hiệu lực (OutstandingToken) của user hiện tại
            tokens = OutstandingToken.objects.filter(user=request.user)
            for token in tokens:
                try:
                    BlacklistedToken.objects.get_or_create(token=token)
                    logout(request)
                except Exception:
                    pass
            #Trả về response thành công, sau khi API run thì user bị logout khỏi tất cả thiết bị
            return Response({
                "success": True,
                "message": "Logged out from all devices successfully"
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#User Profile API
class ProfileView(generics.RetrieveUpdateAPIView): # Đổi từ RetrieveAPIView sang RetrieveUpdateAPIView
    """
    GET /api/v1/user/profile/  -> Xem thông tin
    PUT /api/v1/user/profile/  -> Cập nhật toàn bộ - Update user profile (full)
    PATCH /api/v1/user/profile/-> Cập nhật một phần - Update user profile (partial)
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """
        Method này được gọi khi cần lấy object để thao tác
        """
        # Trả về user đang đăng nhập hiện tại
        return self.request.user
    
    def get_serializer_class(self):
        """Return the serializer class based on the action"""
        if self.request.method in ['PUT', 'PATCH']:
            return ProfileUpdateSerializer
        return UserSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(
        operation_id="user_profile_retrieve",
        summary="Get user profile",
        description="Retrieve the current authenticated user's profile information including nested profile data (patient_profile or doctor_profile based on role).",
        tags=["Accounts"],
        responses={
            200: UserSerializer,
            401: {
                'description': 'Unauthorized - authentication required'
            }
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Override method retrieve để đảm bảo response format đúng
        Handle GET request - trả về user profile với nested profile data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # Refresh from DB để đảm bảo có dữ liệu mới nhất
        instance.refresh_from_db()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="user_profile_update",
        summary="Update user profile",
        description="Update the current authenticated user's profile. Supports both PUT (full update) and PATCH (partial update). Can update nested profile data (patient_profile or doctor_profile).",
        tags=["Accounts"],
        request=ProfileUpdateSerializer,
        responses={
            200: ProfileUpdateSerializer,
            400: {
                'description': 'Validation error',
                'content': {
                    'application/json': {
                        'example': {
                            'field_name': ['Error message']
                        }
                    }
                }
            },
            401: {
                'description': 'Unauthorized - authentication required'
            }
        },
        examples=[
            OpenApiExample(
                'Update Patient Profile',
                value={
                    'full_name': 'John Doe Updated',
                    'phone_num': '0987654321',
                    'patient_profile': {
                        'address': '456 New St',
                        'insurance_id': 'INS123456',
                        'emergency_contact': 'Jane Doe',
                        'emergency_contact_phone': '0123456789'
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                'Update Doctor Profile',
                value={
                    'full_name': 'Dr. Smith Updated',
                    'phone_num': '0987654321',
                    'doctor_profile': {
                        'bio': 'Updated bio information'
                    }
                },
                request_only=True,
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        """
        Override method update để custom response format
        Handle PUT/PATCH request
        """
        partial = kwargs.pop('partial', False) #lấy và xoá key partial từ kwargs
        instance = self.get_object() #lấy user object hiện tại
        
        # Với nested serializer, luôn dùng partial=True để cho phép update một phần
        # Điều này giúp PUT request hoạt động đúng với nested profile
        # Nếu muốn update toàn bộ, vẫn cần gửi đủ fields, nhưng nested sẽ được xử lý linh hoạt hơn
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        #Validate dữ liệu đầu vào
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Refresh from DB để đảm bảo có dữ liệu mới nhất (bao gồm nested profile)
        instance.refresh_from_db()
        
        # Refresh related profile objects nếu có
        if hasattr(instance, 'patient_profile'):
            try:
                instance.patient_profile.refresh_from_db()
            except:
                pass
        if hasattr(instance, 'doctor_profile'):
            try:
                instance.doctor_profile.refresh_from_db()
            except:
                pass
        
        # Return updated user with full profile data
        # Sử dụng ProfileUpdateSerializer với instance để form HTML có thể hiển thị đúng nested fields
        # Browsable API sẽ tự động reload form từ response data
        # Quan trọng: Phải truyền instance vào serializer để __init__ có thể thêm nested fields
        updated_serializer = ProfileUpdateSerializer(instance=instance)
        
        # Trả về response với format mà Browsable API có thể hiểu
        # Response phải trả về chính xác format của serializer để form có thể reload
        return Response(updated_serializer.data, status=status.HTTP_200_OK)


# Doctor List API
class DoctorListView(generics.ListAPIView):
    """
    GET /api/v1/doctors/
    List all active doctors, filterable by department_id
    Query params: 
        - ?department_id=1 (recommended) - Filter by department ID
        - ?specialization=Nhi khoa (backward compatible) - Filter by specialization name
    
    Example:
        GET /api/v1/doctors/?department_id=1 - Get all doctors in department ID 1
        GET /api/v1/doctors/ - Get all active doctors
    """
    from apps.appointments.serializers import DoctorListSerializer
    
    serializer_class = DoctorListSerializer
    permission_classes = [AllowAny]  # Public listing
    
    @extend_schema(
        operation_id="doctors_list",
        summary="List all doctors",
        description="Get a list of all active doctors. Can be filtered by department_id or specialization.",
        tags=["Accounts"],
        parameters=[
            OpenApiParameter(
                name='department_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter doctors by department ID (recommended)',
                required=False,
            ),
            OpenApiParameter(
                name='specialization',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter doctors by specialization name (backward compatible, only used if department_id is not provided)',
                required=False,
            ),
        ],
        responses={
            200: {
                'description': 'List of doctors',
                'content': {
                    'application/json': {
                        'example': [
                            {
                                'id': 1,
                                'full_name': 'Dr. John Smith',
                                'specialization': 'Cardiology',
                                'rating': 4.5,
                                'department': {
                                    'id': 1,
                                    'name': 'Cardiology',
                                    'icon': 'heart'
                                }
                            }
                        ]
                    }
                }
            }
        }
    )
    def get_queryset(self):
        """
        Filter doctors by department_id or specialization if provided
        """
        queryset = Doctor.objects.filter(
            user__is_active=True,
            department__is_active=True  # Chỉ lấy doctors của department đang active
        ).select_related('user', 'department')
        
        # Filter by department_id (preferred method)
        department_id = self.request.query_params.get('department_id', None)
        if department_id:
            try:
                department_id = int(department_id)
                queryset = queryset.filter(department_id=department_id)
            except (ValueError, TypeError):
                # Invalid department_id, return empty queryset
                queryset = queryset.none()
        
        # Filter by specialization (backward compatible - chỉ dùng nếu không có department_id)
        specialization = self.request.query_params.get('specialization', None)
        if specialization and not department_id:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        return queryset.order_by('-rating', 'user__full_name')
    

class ForgotPasswordView(APIView):
    """
    API to request password reset
    POST /api/v1/auth/forgot-password/
    """
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer
    
    @extend_schema(
        operation_id="auth_reset_password",
        summary="Reset password",
        description="Reset user password using valid reset token.",
        tags=["Authentication"],
        request=ResetPasswordSerializer,
        responses={
            200: {
                'description': 'Password reset successful',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Password has been reset successfully. You can now login with your new password.'
                        }
                    }
                }
            },
            400: {
                'description': 'Validation error',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'message': 'Failed to reset password',
                            'errors': {
                                'confirm_password': ['Passwords do not match']
                            }
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Reset Password Request',
                value={
                    'uid': 'MQ',
                    'token': 'c6v8xq-1234567890abcdef1234567890ab',
                    'new_password': 'newpassword123',
                    'confirm_password': 'newpassword123'
                },
                request_only=True,
            )
        ]
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Password has been reset successfully. You can now login with your new password."
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "message": "Failed to reset password",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ResetPasswordView.post: {str(e)}", exc_info=True)
            return Response({
                "success": False,
                "message": "An error occurred while resetting password. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )