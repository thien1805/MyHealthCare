from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError as DRFValidationError
from .models import User
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, ProfileUpdateSerializer, DoctorProfileSerializer, PatientProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate, get_user_model
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
    POST /api/accounts/login/
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

            return Response({
                "success": True,
                "message": "Logout successfully"
            }, status=status.HTTP_205_RESET_CONTENT)

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
    GET /api/v1/auth/profile/  -> Xem thông tin
    PUT /api/v1/auth/profile/  -> Cập nhật toàn bộ - Update user profile (full)
    PATCH /api/v1/auth/profile/-> Cập nhật một phần - Update user profile (partial)
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

    def update(self, request, *args, **kwargs):
        """
        Override method update để custom response format
        Handle PUT/PATCH request
        """
        partial = kwargs.pop('partial', False) #lấy và xoá key partial từ kwargs
        instance = self.get_object() #lấy user object hiện tại
        
        #tạo serializer với
        # -instance: object cần update 
        # -data: dữ liệu mới từ request body
        # -partial: cho phép update một phần hay không
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        #Validate dữ liệu đầu vào
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        #Return updated user with full profule data
        updated_user = UserSerializer(instance).data
        
        return Response({
            "success": True,
            "message": "Profile updated successfully",
            "user": updated_user
        }, status=status.HTTP_200_OK)
    

            
            
            
            
            
    
       

        