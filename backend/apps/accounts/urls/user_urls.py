from django.urls import path
from apps.accounts.views import ProfileView

app_name = 'user'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
] 

