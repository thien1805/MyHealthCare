from django.urls import path
from apps.accounts.views import DoctorListView

urlpatterns = [
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
]

