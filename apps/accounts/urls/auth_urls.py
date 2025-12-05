from django.urls import path
from apps.accounts.views import RegisterView, LoginView, LogoutView, LogoutAllView, ForgotPasswordView, VerifyResetTokenView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout-all'),
    
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-reset-token/', VerifyResetTokenView.as_view(), name='verify-reset-token'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
] 

