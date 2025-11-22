from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError as DRFValidationError
from .models import User, Doctor
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, ProfileUpdateSerializer, DoctorProfileSerializer, PatientProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.conf import settings
from django.apps import apps
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import logging

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
                "error": str(e) if settings.DEBUG else "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
#Login API
class LoginView(generics.GenericAPIView):
    """
    POST /api/v1/auth/login/
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
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