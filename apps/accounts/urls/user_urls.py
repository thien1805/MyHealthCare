from django.urls import path
from apps.accounts.views import ProfileView


urlpatterns = [
    path('me/', ProfileView.as_view(), name='me'),
] 

