from django.urls import path
from .views import AvailableSlotsView

# Note: ServiceViewSet and AppointmentViewSet are registered in main urls.py
# to enable browsable API root view

urlpatterns = [
    # Custom action URLs (not part of ViewSet)
    path('available-slots/', AvailableSlotsView.as_view(), name='available-slots'),
]

