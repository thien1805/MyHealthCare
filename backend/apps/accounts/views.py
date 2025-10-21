from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models import User
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import authenticate, get_user_model
#Registration API 

User = get_user_model()
class RegisterView(generics.CreateAPIView):
    """
    API to register a new patient
    POST /api/accounts/register/
    """
    query_set = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] #anyone can access this API
    
    def create(self, request, *args, **kwargs):
        #validate input
        serializer = self.get_serializer(data=request.data) #initial_data (raw data from request)
        serializer.is_valid(raise_exception=True) #call validate method, if not valid, raise exception
        #create user
        user = serializer.save() #call create method in register serializer
        
        #create the JWT token for the new user
        refresh = RefreshToken.for_user(user)
        return Response({
            "success": True,
            "message": "User registered successfully",
            "user": UserSerializer(user).data,
            "tokens":
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token) #access token
                }
        }, status=status.HTTP_201_CREATED)
        
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
        user = authenticate(email=email, password=password)
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
        
#User Profile API
class ProfileView(generics.RetrieveAPIView):
    """
    GET /api/accounts/profile/
    PUT /api/accounts/profile
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] #Must be logged in to access this API
    
    def get_object(self):
        return self.request.user
        