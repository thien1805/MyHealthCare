from django.urls import path, include

app_name = 'accounts'

urlpatterns = [
    path('auth/', include('apps.accounts.urls.auth_urls')),
    path('user/', include('apps.accounts.urls.user_urls')),
    path('', include('apps.accounts.urls.doctor_urls')),  # /api/v1/doctors/
]

