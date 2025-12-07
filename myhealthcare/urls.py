"""
URL configuration for myhealthcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from apps.accounts.views import ProfileView
from apps.appointments.views import ServiceViewSet, AppointmentViewSet, DepartmentViewSet, AvailableSlotsView, SuggestDepartmentView, HealthChatbotView

# Create main API router for browsable API root
api_router = DefaultRouter()
api_router.register(r'departments', DepartmentViewSet, basename='department')
api_router.register(r'services', ServiceViewSet, basename='service')
api_router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    
    #OpenAPI Schema 
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    #Swagger UI (Interactiver API documentation)
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    #Redoc (Alternative documentation UI)
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Custom appointments URLs (must be before router to avoid conflicts)
    path('api/v1/appointments/available-slots/', AvailableSlotsView.as_view(), name='available-slots'),
    path('api/v1/appointments/suggest-department/', SuggestDepartmentView.as_view(), name='suggest-department'),
    path('api/v1/ai/health-qa/', HealthChatbotView.as_view(), name='health-chatbot'),    #AI service URLs


    # API Root - Browsable API interface (shows all available endpoints)
    path('api/v1/', include(api_router.urls)),
    
    # Accounts URLs
    path('api/v1/', include('apps.accounts.urls'), name='accounts'),
    
    # Appointments custom URLs (available-slots, etc.)
    path('api/v1/', include('apps.appointments.urls'), name='appointments'),  # Appointments APIs
    
    # JWT Authentication endpoints
    # Endpoint để lấy cả access và refresh token
    # POST yêu cầu username và password
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Endpoint để làm mới (refresh) ACCESS Token đã hết hạn
    # POST yêu cầu refresh token
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]


