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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.accounts.views import ProfileView

urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/auth/', include(('apps.accounts.urls.auth_urls'), namespace='auth')),
    path('api/v1/user', include(('apps.accounts.urls.user_urls'), namespace='user')),
    #Endpoint đeer lấy cả access và refresh token
    # post yêu cầu username và password
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    #Endpoint để làm mới (refresh) ACCESS Token đã hết hạn
    #POST yêu cầu refresh token
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


