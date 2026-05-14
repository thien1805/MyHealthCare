from typing import Any
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, time as dt_time
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Department, Service, Room, Appointment, MedicalRecord
from .serializers import (
    DepartmentSerializer,
    ServiceSerializer,
    RoomSerializer,
    AvailableSlotSerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentRescheduleSerializer,
    AppointmentCancelSerializer,
    AppointmentAssignServiceSerializer,
    DepartmentDetailSerializer,
    MedicalRecordSerializer,
    MedicalRecordCreateUpdateSerializer
)

User = get_user_model()

class StandardResultSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = "page"

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Department model
    GET /api/v1/departments/ - List all active departments
    GET /api/v1/departments/{id}/ - Retrieve a department
    """
    queryset = Department.objects.filter(is_active=True).order_by('name')
    permission_classes = [AllowAny]  # Public listing
    pagination_class = StandardResultSetPagination
    
    @extend_schema(
        operation_id="departments_list",
        summary="List all active medical departments",
        description="""Get paginated list of all hospital departments with basic information.
        
        **Department Structure:**
        Departments organize medical specialties and group doctors by expertise:
        - Cardiology: Heart and cardiovascular system
        - Pediatrics: Children's healthcare
        - Orthopedics: Bones, joints, muscles
        - Dermatology: Skin conditions
        - Neurology: Nervous system
        - Internal Medicine: General adult healthcare
        
        **Returned Data Per Department:**
        - `id`: Unique department identifier
        - `name`: Department name (e.g., "Cardiology")
        - `description`: Overview of services provided
        - `icon`: Icon name for UI display (e.g., "heart", "baby", "bone")
        - `health_examination_fee`: Base consultation fee (VND)
        - `is_active`: Whether department is currently operational
        
        **Filtering:**
        - Only active departments (`is_active=True`) are returned
        - Inactive departments are hidden from public view
        
        **Pagination:**
        - Default page size: 10 departments
        - Maximum page size: 100 departments
        - Query parameters: `page`, `page_size`
        - Response includes: count, next, previous, results
        
        **Sorting:**
        - Departments ordered by name (alphabetically)
        - Consistent ordering across requests
        
        **Health Examination Fee:**
        - Base consultation fee charged by department
        - Does NOT include additional services (X-Ray, tests, etc.)
        - Services add to total fee after consultation
        
        **Use Cases:**
        - Appointment booking: Show department selection dropdown
        - Homepage: Display available medical specialties
        - Search/Filter: Help patients find right department
        - Department directory: Public information page
        
        **Example Response:**
        ```json
        {
          "count": 8,
          "next": null,
          "previous": null,
          "results": [
            {
              "id": 1,
              "name": "Cardiology",
              "description": "Heart and cardiovascular care",
              "icon": "heart",
              "health_examination_fee": "500000.00",
              "is_active": true
            },
            ...
          ]
        }
        ```
        
        **Best Practices:**
        - Cache department list (changes infrequently)
        - Display icon for better UX
        - Show health_examination_fee upfront (transparency)
        - Use for dynamic department selection in forms
        
        **Note:**
        For detailed department info including doctors and services, use the retrieve endpoint.
        """,
        tags=["Departments"],
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number',
                required=False,
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of results per page (max 100)',
                required=False,
            ),
        ],
        responses={
            200: DepartmentSerializer(many=True),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="departments_retrieve",
        summary="Get comprehensive department details with doctors and services",
        description="""Retrieve complete information about a department including all associated doctors and services.
        
        **Detailed Department Information:**
        Uses DepartmentDetailSerializer which includes:
        
        **Basic Info:**
        - id, name, description
        - icon (for UI display)
        - health_examination_fee (base consultation cost)
        - is_active status
        
        **Associated Doctors:**
        Complete list of doctors working in this department:
        - Doctor's full name and specialization
        - Professional title (Professor, Associate Professor, etc.)
        - Rating and total reviews
        - Avatar URL
        - Bio/background
        - Assigned room
        - Years of experience (if available)
        
        **Available Services:**
        All medical services offered by this department:
        - Service name and description
        - Service price (additional to examination fee)
        - Service icon
        - Availability status
        - Service category
        
        **Use Cases:**
        
        1. **Department Detail Page:**
           - Show complete department profile
           - List all doctors in department
           - Display available services and prices
           
        2. **Doctor Selection:**
           - Patient views cardiology department
           - Sees all cardiologists with ratings
           - Chooses preferred doctor for booking
           
        3. **Service Discovery:**
           - Patient exploring orthopedics
           - Views available services (X-Ray, MRI, Physical Therapy)
           - Understands total potential costs
           
        4. **Price Transparency:**
           - Base examination fee from department
           - Individual service prices listed
           - Patient can estimate total cost
        
        **Data Relationships:**
        - Department → Many Doctors (one department, multiple doctors)
        - Department → Many Services (department offers multiple services)
        - Department → Many Rooms (department has multiple rooms)
        
        **Doctor Information Included:**
        Helps patients choose the right doctor:
        - Rating: Average patient satisfaction (0-5 stars)
        - Specialization: Specific medical expertise
        - Experience: Professional background
        - Room: Where to find the doctor
        
        **Service Information Included:**
        Helps patients understand offerings:
        - Name: Service title (e.g., "ECG", "Blood Test")
        - Price: Additional cost beyond examination fee
        - Description: What the service involves
        
        **Response Structure:**
        ```json
        {
          "id": 1,
          "name": "Cardiology",
          "description": "Comprehensive heart care",
          "icon": "heart",
          "health_examination_fee": "500000.00",
          "is_active": true,
          "doctors": [
            {
              "id": 5,
              "full_name": "Dr. John Smith",
              "specialization": "Interventional Cardiology",
              "rating": 4.8,
              "total_reviews": 142,
              "avatar_url": "https://...",
              "room": { "room_number": "201", ... }
            }
          ],
          "services": [
            {
              "id": 10,
              "name": "ECG (Electrocardiogram)",
              "price": "150000.00",
              "description": "Heart electrical activity test"
            }
          ]
        }
        ```
        
        **Best Practices:**
        - Use this endpoint for department detail pages
        - Display doctors sorted by rating
        - Show total cost breakdown (examination + services)
        - Cache response (department details change rarely)
        
        **Error Handling:**
        - 404: Department not found or inactive
        - Returns error even if department exists but is_active=False
        
        **Difference from List Endpoint:**
        - List: Basic info only, all departments
        - Retrieve: Complete info including doctors/services, one department
        - List: For dropdown/directory
        - Retrieve: For detail page
        """,
        tags=["Departments"],
        responses={
            200: DepartmentDetailSerializer,
            404: {
                'description': 'Department not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found.'
                        }
                    }
                }
            }
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == "retrieve":
            return DepartmentDetailSerializer
        return DepartmentSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Service model
    GET /api/v1/services/ - List all active services
    GET /api/v1/services/{id}/ - Retrieve a service
    GET /api/v1/services/?department_id=1 - Filter by department ID
    GET /api/v1/services/?specialty_id=1 - Filter by service ID
    """
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]  # Public listing
    
    @extend_schema(
        operation_id="services_list",
        summary="List medical services",
        description="""Get list of all active medical services with optional filtering.
        
        **Services vs Departments:**
        - Department: Medical specialty (e.g., Cardiology, Pediatrics)
        - Service: Specific procedures within department (e.g., ECG, Blood Test)
        - Each service belongs to exactly one department
        
        **Query Parameters:**
        - `department_id`: Filter services by department (recommended)
        - `specialty_id`: Legacy parameter, filters by service ID directly
        
        **Response Includes:**
        - Service details: id, name, description, price
        - Department info: id, name, icon
        - Availability status: is_active
        
        **Use Cases:**
        - Patient booking: Show services available in selected department
        - Price inquiry: List services with consultation fees
        - Service catalog: Browse all available medical services
        
        **Pricing Note:** 
        - Service price is additional to base consultation fee
        - Service is assigned by doctor after examination
        - Not required when booking appointment
        """,
        tags=["Services"],
        parameters=[
            OpenApiParameter(
                name='department_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter services by department ID',
                required=False,
            ),
            OpenApiParameter(
                name='specialty_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter services by service ID (specialty)',
                required=False,
            ),
        ],
        responses={
            200: ServiceSerializer(many=True),
            400: {
                'description': 'Invalid query parameters',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'error': "Invalid department_id: 'abc'. Must be an integer."
                        }
                    }
                }
            },
            404: {
                'description': 'Department or service not found',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'error': 'Department with ID 999 not found or inactive'
                        }
                    }
                }
            }
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="services_retrieve",
        summary="Get detailed information about a specific medical service",
        description="""Retrieve complete details of a single service by ID.
        
        **Service Information Includes:**
        - `id`: Unique service identifier
        - `name`: Service name (e.g., "X-Ray Imaging", "Complete Blood Count")
        - `description`: Detailed explanation of the service
        - `price`: Cost in VND (additional to examination fee)
        - `icon`: Icon name for UI display
        - `is_active`: Whether service is currently offered
        - `department`: Parent department information
          - Department id, name, icon
          - Helps understand service context
        
        **Use Cases:**
        - Service detail page: Show complete service information
        - Price inquiry: Display exact service cost
        - Service comparison: Compare different services
        - Patient education: Explain what service involves
        - Booking reference: Link from appointment to service details
        
        **Cost Structure:**
        - Service price is ADDITIONAL to base examination fee
        - Example calculation:
          - Base examination: 500,000 VND (department fee)
          - X-Ray service: 200,000 VND (this service price)
          - Total: 700,000 VND
        
        **Service Assignment Context:**
        - Services are NOT selected during appointment booking
        - Doctor assigns services AFTER examining patient
        - Ensures appropriate tests are ordered based on diagnosis
        - Prevents unnecessary service bookings
        
        **Response Example:**
        ```json
        {
          "id": 15,
          "name": "Chest X-Ray",
          "description": "Diagnostic imaging of chest cavity to examine lungs, heart, and chest wall",
          "price": "200000.00",
          "icon": "x-ray",
          "is_active": true,
          "department": {
            "id": 3,
            "name": "Radiology",
            "icon": "scan"
          }
        }
        ```
        
        **Department Context:**
        Service details include department info because:
        - Services are department-specific
        - Helps understand medical specialty context
        - Useful for organizing services in UI
        - Validates doctor can assign (must match appointment department)
        
        **Error Handling:**
        - 404: Service not found
        - Inactive services (is_active=False) may also return 404
        - Ensures only available services are shown
        
        **Best Practices:**
        - Display service with department context
        - Show price clearly (transparency)
        - Explain description to patient
        - Link to related services in same department
        - Use for patient education about procedures
        
        **Note:**
        For listing multiple services, use the list endpoint with optional department_id filter.
        """,
        tags=["Services"],
        responses={
            200: ServiceSerializer,
            404: {
                'description': 'Service not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found.'
                        }
                    }
                }
            }
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="services_specialties",
        summary="List all specialties/departments",
        description="Get a list of all unique specialties/departments (alias for departments list)",
        tags=["Services"],
        responses={
            200: DepartmentSerializer(many=True),
        }
    )
    @action(detail=False, methods=['get'], url_path='specialties')
    def specialties(self, request):
        """
        GET /api/v1/services/specialties/
        List all unique specialties/departments
        """
        departments = Department.objects.filter(is_active=True).order_by('name')
        serializer = DepartmentSerializer(departments, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        """
        Filter services by specialty_id or department_id if provided
        """
        queryset = super().get_queryset()
        
        specialty_id = self.request.query_params.get('specialty_id', None)
        department_id = self.request.query_params.get('department_id', None)
        
        # Filter by specialty_id (service ID)
        if specialty_id:
            try:
                specialty_id = int(specialty_id)
                queryset = queryset.filter(id=specialty_id)
            except (ValueError, TypeError):
                # Invalid specialty_id - will be handled in list() method
                pass
        
        # Filter by department_id
        if department_id:
            try:
                department_id = int(department_id)
                queryset = queryset.filter(department_id=department_id)
            except (ValueError, TypeError):
                # Invalid department_id - will be handled in list() method
                pass
        
     
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list to validate query parameters before filtering
        """
        specialty_id = request.query_params.get('specialty_id', None)
        department_id = request.query_params.get('department_id', None)
        
        # Validate specialty_id if provided
        if specialty_id:
            try:
                specialty_id_int = int(specialty_id)
                # Check if service exists
                if not Service.objects.filter(id=specialty_id_int, is_active=True).exists():
                    return Response({
                        "success": False,
                        "error": f"Service with ID {specialty_id} not found or inactive"
                    }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                return Response({
                    "success": False,
                    "error": f"Invalid specialty_id: '{specialty_id}'. Must be an integer."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate department_id if provided
        if department_id:
            try:
                department_id_int = int(department_id)
                # Check if department exists
                if not Department.objects.filter(id=department_id_int, is_active=True).exists():
                    return Response({
                        "success": False,
                        "error": f"Department with ID {department_id} not found or inactive"
                    }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                return Response({
                    "success": False,
                    "error": f"Invalid department_id: '{department_id}'. Must be an integer."
                }, status=status.HTTP_400_BAD_REQUEST)
      
        # If validation passes, call parent list method
        return super().list(request, *args, **kwargs)


class AvailableSlotsView(APIView):
    """
    GET /api/v1/appointments/available-slots/
    Get available time slots for a doctor on a specific date
    Query params: doctor_id, date, department_id (optional)
    """
    permission_classes = [AllowAny]  # Public access for booking
    
    @extend_schema(
        operation_id="appointments_available_slots",
        summary="Check doctor's available time slots",
        description="""Get all time slots for a doctor on specific date with availability status.
        
        **Time Slot System:**
        - Operating hours: 08:00 - 16:30
        - Slot duration: 30 minutes
        - Total slots per day: 18 slots
        - Format: HH:MM (e.g., "08:00", "08:30")
        
        **Availability Logic:**
        - available=True: Slot is free, can book
        - available=False: Slot already booked by another patient
        - Returns ALL slots regardless of availability
        
        **Booking Rules:**
        - Cannot book past dates
        - Cannot book more than 30 days in advance
        - Cannot book already taken slots
        - One patient per slot per doctor
        
        **Room Assignment:**
        - Shows default room for available slots
        - Room is auto-assigned when booking
        - Priority: Doctor's dedicated room > Department room
        
        **Use Cases:**
        - Patient booking: Display available times for doctor selection
        - Calendar view: Show doctor's schedule
        - Conflict prevention: Real-time slot availability check
        
        **Required Parameters:**
        - `doctor_id`: Doctor's user ID
        - `date`: Appointment date (YYYY-MM-DD)
        
        **Optional Parameters:**
        - `department_id`: Filter by department (for validation)
        """,
        tags=["Appointments"],
        parameters=[
            OpenApiParameter(
                name='doctor_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Doctor ID',
                required=True,
            ),
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Appointment date in YYYY-MM-DD format',
                required=True,
            ),
            OpenApiParameter(
                name='department_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Department ID (optional)',
                required=False,
            ),
        ],
        responses={
            200: {
                'description': 'Available slots retrieved successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'date': '2024-01-15',
                            'doctor': {
                                'id': 1,
                                'full_name': 'Dr. John Doe',
                                'specialization': 'Cardiology'
                            },
                            'department': {
                                'id': 1,
                                'name': 'Cardiology',
                                'icon': 'heart'
                            },
                            'available_slots': [
                                {
                                    'time': '08:00',
                                    'available': True,
                                    'room': '101'
                                },
                                {
                                    'time': '08:30',
                                    'available': False,
                                    'room': None
                                }
                            ]
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid request parameters',
                'content': {
                    'application/json': {
                        'examples': {
                            'missing_params': {
                                'value': {
                                    'success': False,
                                    'error': 'doctor_id and date are required parameters'
                                }
                            },
                            'invalid_date': {
                                'value': {
                                    'success': False,
                                    'error': 'Invalid date format. Use YYYY-MM-DD'
                                }
                            },
                            'past_date': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot book appointments in the past'
                                }
                            },
                            'too_far_ahead': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot book appointments more than 30 days in advance'
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Doctor or department not found',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'error': 'Doctor not found or inactive'
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """
        Calculate and return available time slots
        """
        doctor_id = request.query_params.get('doctor_id')
        date_str = request.query_params.get('date')
        department_id = request.query_params.get('department_id')
        
        # Validate required parameters
        if not doctor_id or not date_str:
            return Response({
                "success": False,
                "error": "doctor_id and date are required parameters"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            doctor = User.objects.get(id=doctor_id, role='doctor', is_active=True)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "Doctor not found or inactive"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                "success": False,
                "error": "Invalid date format. Use YYYY-MM-DD"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Business rules validation
        today = timezone.now().date()
        if appointment_date < today:
            return Response({
                "success": False,
                "error": "Cannot book appointments in the past"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        max_date = today + timedelta(days=30)
        if appointment_date > max_date:
            return Response({
                "success": False,
                "error": "Cannot book appointments more than 30 days in advance"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate department_id if provided
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id, is_active=True)
            except Department.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "Department not found or inactive"
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Default slot duration (30 minutes)
        slot_duration = 30
        
        # Generate all possible time slots (08:00 - 16:30, 30-minute intervals)
        start_time = dt_time(8, 0)
        end_time = dt_time(16, 30)
        all_slots = []
        
        current_time = datetime.combine(appointment_date, start_time).time()
        end_datetime = datetime.combine(appointment_date, end_time)
        
        while current_time <= end_time:
            all_slots.append(current_time)
            current_datetime = datetime.combine(appointment_date, current_time)
            current_datetime += timedelta(minutes=slot_duration)
            current_time = current_datetime.time()
        
        # Get booked appointments for this doctor on this date
        booked_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=['booked', 'confirmed']
        ).values_list('appointment_time', flat=True)
        
        # Get available rooms for the department if provided, otherwise get any available room
        if department:
            available_rooms = Room.objects.filter(
                department=department,
                is_active=True
            ).first()
        else:
            available_rooms = Room.objects.filter(is_active=True).first()
        default_room = available_rooms.room_number if available_rooms else None
        
        # Build response
        available_slots_data = []
        for slot_time in all_slots:
            is_available = slot_time not in booked_appointments
            available_slots_data.append({
                "time": slot_time.strftime("%H:%M"),
                "available": is_available,
                "room": default_room if is_available else None
            })
        
        # Get doctor info
        doctor_profile = doctor.doctor_profile
        doctor_info = {
            "id": doctor.id,
            "full_name": doctor.full_name,
            "specialization": doctor_profile.specialization
        }
        
        # Get department info if provided
        department_info = None
        if department:
            department_info = {
                "id": department.id,
                "name": department.name,
                "icon": department.icon
            }
        
        serializer = AvailableSlotSerializer(available_slots_data, many=True)
        
        response_data = {
            "date": date_str,
            "doctor": doctor_info,
            "available_slots": serializer.data
        }
        
        if department_info:
            response_data["department"] = department_info
        
        return Response(response_data, status=status.HTTP_200_OK)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Appointment model
    POST /api/v1/appointments/ - Book new appointment
    GET /api/v1/appointments/my-appointments/ - Get patient's appointments
    POST /api/v1/appointments/{id}/cancel/ - Cancel appointment
    PUT /api/v1/appointments/{id}/reschedule/ - Reschedule appointment
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultSetPagination
    
    def get_serializer_class(self):
        """
        Use different serializer for different actions
        """
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action == 'cancel':
            return AppointmentCancelSerializer
        elif self.action == 'reschedule':
            return AppointmentRescheduleSerializer
        elif self.action == 'create_medical_record':
            return MedicalRecordCreateUpdateSerializer
        return AppointmentSerializer
    
    @extend_schema(
        operation_id="appointments_create",
        summary="Book a new appointment",
        description="""Create a new appointment for a patient with a doctor at specific date and time.
        
        **Authorization & Permissions:**
        - Only authenticated patients can book appointments
        - Doctors and admins cannot book appointments (403 error)
        - JWT token required in Authorization header
        
        **Booking Process:**
        1. Patient selects department (optional but recommended)
        2. Patient chooses doctor from department or available doctors list
        3. System checks available time slots for selected date
        4. Patient selects available time slot
        5. Patient fills symptoms, reason, and optional notes
        6. System validates slot availability (real-time check)
        7. Room is auto-assigned (doctor's room or department room)
        8. Appointment created with status='booked'
        
        **Required Fields:**
        - `doctor_id`: ID of the doctor to book with
        - `appointment_date`: Date in YYYY-MM-DD format
        - `appointment_time`: Time in HH:MM:SS format (e.g., "09:00:00")
        - `symptoms`: Patient's current symptoms/complaints
        
        **Optional Fields:**
        - `department_id`: Department ID (for validation)
        - `reason`: Additional reason for visit
        - `notes`: Any extra information for doctor
        
        **Validation Rules:**
        - Time slot must be available (not already booked)
        - Cannot book past dates
        - Cannot book more than 30 days in advance
        - Time must be within operating hours (08:00-16:30)
        - Doctor must be active and exist
        - Department must be active (if provided)
        
        **Room Assignment Logic:**
        - Priority 1: Doctor's dedicated room
        - Priority 2: Department's available room
        - Priority 3: Any active room
        
        **Fee Calculation:**
        - Based on doctor's assigned services
        - Returned as `estimated_fee` in response
        - Actual fee may vary after consultation
        
        **Response Data:**
        - Complete appointment details
        - Patient information
        - Doctor information with specialization
        - Assigned room information
        - Appointment status (initially 'booked')
        - Estimated consultation fee
        
        **Status Workflow:**
        - booked → confirmed → completed
        - Or: booked → cancelled
        
        **Use Cases:**
        - Online appointment booking by patients
        - Walk-in registration by reception staff
        - Telemedicine appointment scheduling
        - Follow-up appointment booking
        """,
        tags=["Appointments"],
        request=AppointmentCreateSerializer,
        responses={
            201: {
                'description': 'Appointment booked successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Appointment booked successfully',
                            'appointment': {
                                'id': 1,
                                'patient': {
                                    'id': 1,
                                    'full_name': 'John Doe',
                                    'email': 'patient@example.com'
                                },
                                'doctor': {
                                    'id': 2,
                                    'full_name': 'Dr. Jane Smith',
                                    'specialization': 'Cardiology'
                                },
                                'appointment_date': '2024-01-15',
                                'appointment_time': '09:00:00',
                                'status': 'booked',
                                'estimated_fee': '500000.00'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Validation error',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'error': 'This time slot is already taken. Please choose another time.'
                        }
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'error': 'Only patients can book appointments'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Book Appointment Example',
                value={
                    'doctor_id': 2,
                    'department_id': 1,
                    'appointment_date': '2024-01-15',
                    'appointment_time': '09:00:00',
                    'symptoms': 'Chest pain',
                    'reason': 'Regular checkup',
                    'notes': 'First time visit'
                },
                request_only=True,
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="appointments_list",
        summary="List appointments with role-based filtering",
        description="""Get paginated list of appointments with automatic role-based filtering.
        
        **Role-Based Access Control:**
        - **Patients**: See only their own appointments (auto-filtered by user ID)
        - **Doctors**: See only appointments assigned to them (auto-filtered by doctor ID)
        - **Admins**: See all appointments in the system (no filtering)
        
        **Appointment Data Includes:**
        - Patient information (full name, email, phone)
        - Doctor information (full name, specialization, department)
        - Appointment date and time
        - Status (booked, confirmed, completed, cancelled)
        - Department and room details
        - Symptoms and reason for visit
        - Medical record ID (if created)
        - Fee information (estimated and actual)
        - Notes from patient and doctor
        
        **Pagination:**
        - Default page size: 10 results
        - Maximum page size: 100 results
        - Response includes: count, next, previous, results
        
        **Sorting:**
        - Default: Most recent appointments first
        - Order by: appointment_date (descending), then appointment_time (descending)
        - Newest bookings appear at the top
        
        **Status Values:**
        - `booked`: Initially created, awaiting confirmation
        - `confirmed`: Doctor/staff confirmed the appointment
        - `completed`: Appointment finished, may have medical record
        - `cancelled`: Cancelled by patient or doctor
        
        **Query Parameters:**
        - `page`: Page number (default: 1)
        - `page_size`: Results per page (default: 10, max: 100)
        
        **Use Cases:**
        - Patient dashboard: View appointment history
        - Doctor schedule: See daily/weekly appointments
        - Admin management: Monitor all appointments
        - Appointment calendar: Display in calendar view
        - Receptionist desk: Check today's appointments
        
        **Response Structure:**
        ```json
        {
          "count": 25,
          "next": "http://api.../appointments/?page=2",
          "previous": null,
          "results": [...]
        }
        ```
        """,
        tags=["Appointments"],
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number',
                required=False,
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of results per page (max 100)',
                required=False,
            ),
        ],
        responses={
            200: AppointmentSerializer(many=True),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="appointments_retrieve",
        summary="Retrieve detailed appointment information",
        description="""Get complete details of a specific appointment by ID.
        
        **Access Control:**
        - Patients: Can view only their own appointments
        - Doctors: Can view only appointments assigned to them
        - Admins: Can view any appointment
        - 404 error if appointment doesn't exist or user lacks permission
        
        **Detailed Information Included:**
        - **Patient Details:**
          - Full name, email, phone number
          - Date of birth, gender
          - Emergency contact information
          - Insurance ID
        
        - **Doctor Details:**
          - Full name, specialization
          - Department affiliation
          - Room assignment
          - Rating and reviews count
        
        - **Appointment Info:**
          - Date and time
          - Status (booked/confirmed/completed/cancelled)
          - Room number and department
          - Created and updated timestamps
        
        - **Medical Details:**
          - Patient's symptoms
          - Reason for visit
          - Patient notes
          - Doctor notes (if any)
        
        - **Financial Info:**
          - Estimated consultation fee
          - Actual fee charged (if completed)
        
        - **Medical Record:**
          - Medical record ID (if created)
          - Link to full medical record details
        
        **Use Cases:**
        - Appointment detail page
        - Patient viewing booking confirmation
        - Doctor reviewing pre-appointment info
        - Admin checking appointment specifics
        - Receptionist verifying patient arrival
        
        **Status Interpretation:**
        - `booked`: Awaiting confirmation, patient can cancel
        - `confirmed`: Confirmed by staff, patient should attend
        - `completed`: Visit finished, check for medical record
        - `cancelled`: No longer active, reason may be in notes
        
        **Response Example:**
        Returns complete AppointmentSerializer data with nested relationships.
        """,
        tags=["Appointments"],
        responses={
            200: AppointmentSerializer,
            404: {
                'description': 'Appointment not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found.'
                        }
                    }
                }
            }
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="appointments_doctors_by_department",
        summary="Get available doctors filtered by department",
        description="""Retrieve list of active doctors who belong to a specific department.
        
        **Purpose:**
        Used for dynamic form population when patient selects a department during appointment booking.
        
        **Process Flow:**
        1. Patient selects department from dropdown
        2. Frontend calls this endpoint with department_id
        3. Backend returns all doctors in that department
        4. Frontend populates doctor dropdown with results
        5. Patient selects doctor to proceed with booking
        
        **Department-Doctor Relationship:**
        - Each doctor belongs to one primary department
        - Departments group doctors by medical specialty
        - Examples: Cardiology, Pediatrics, Orthopedics, etc.
        - Only active doctors and departments are returned
        
        **Filtering Logic:**
        - Filters by `department_id` (required parameter)
        - Only includes active doctors (`is_active=True`)
        - Only includes active departments (`is_active=True`)
        - Results sorted by rating (highest first), then alphabetically
        
        **Required Query Parameter:**
        - `department_id`: Integer ID of the department
        
        **Validation:**
        - department_id must be provided (400 error if missing)
        - department_id must be valid integer (400 error if invalid)
        - Department must exist and be active (404 error if not found)
        
        **Response Data:**
        - **Department info**: id, name, icon
        - **Doctors array**: Each doctor includes:
          - id: Doctor's user ID (for booking)
          - full_name: Dr. [Name]
          - specialization: Medical specialty
          - rating: Average patient rating (0-5)
          - total_reviews: Number of reviews
          - avatar_url: Profile picture URL
          - title: Professional title (e.g., "Professor", "Associate Professor")
          - bio: Short biography
          - room: Assigned room information
        - **Count**: Total number of doctors in department
        
        **Use Cases:**
        - Appointment booking form: Populate doctor dropdown
        - Department page: Show all doctors in department
        - Doctor search: Filter by medical specialty
        - Patient choice: Compare doctors by rating
        
        **Best Practices:**
        - Call this endpoint when department selection changes
        - Cache results to reduce API calls
        - Display doctor rating to help patient choose
        - Show specialization for clarity
        
        **Example Workflow:**
        ```
        1. User selects "Cardiology" (department_id=1)
        2. GET /api/v1/appointments/doctors-by-department/?department_id=1
        3. Receives list of cardiologists
        4. User selects "Dr. John Smith" (id=5)
        5. Proceeds to date/time selection
        ```
        """,
        tags=["Appointments"],
        parameters=[
            OpenApiParameter(
                name='department_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Department ID',
                required=True,
            ),
        ],
        responses={
            200: {
                'description': 'Doctors retrieved successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'department': {
                                'id': 1,
                                'name': 'Cardiology',
                                'icon': 'heart'
                            },
                            'doctors': [
                                {
                                    'id': 1,
                                    'full_name': 'Dr. John Doe',
                                    'specialization': 'Cardiology',
                                    'rating': 4.5
                                }
                            ],
                            'count': 1
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid request',
                'content': {
                    'application/json': {
                        'example': {
                            'error': 'department_id parameter is required'
                        }
                    }
                }
            },
            404: {
                'description': 'Department not found',
                'content': {
                    'application/json': {
                        'example': {
                            'error': 'Department with ID 999 not found or inactive.'
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='doctors-by-department', permission_classes=[IsAuthenticated])
    def doctors_by_department(self, request):
        """
        GET /api/v1/appointments/doctors-by-department/?department_id=1
        Get list of doctors filtered by department_id
        Useful for HTML form to dynamically load doctors when department is selected
        """
        from apps.accounts.models import Doctor
        from apps.appointments.serializers import DoctorListSerializer
        
        department_id = request.query_params.get('department_id')
        
        if not department_id:
            return Response({
                'error': 'department_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            department_id = int(department_id)
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid department_id. Must be an integer.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if department exists
        try:
            department = Department.objects.get(id=department_id, is_active=True)
        except Department.DoesNotExist:
            return Response({
                'error': f'Department with ID {department_id} not found or inactive.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get doctors from this department
        doctors = Doctor.objects.filter(
            department_id=department_id,
            user__is_active=True
        ).select_related('user', 'department').order_by('-rating', 'user__full_name')
        
        serializer = DoctorListSerializer(doctors, many=True)
        
        return Response({
            'department': {
                'id': department.id,
                'name': department.name,
                'icon': department.icon
            },
            'doctors': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    
    def get_queryset(self): 
        """
        Filter appointments based on user role
        """
        user = self.request.user
        
        if user.role == 'patient':
            # Patients can only see their own appointments
            return Appointment.objects.filter(patient=user).order_by('-appointment_date', 'appointment_time')
        elif user.role == 'doctor':
            # Doctors can see their appointments
            return Appointment.objects.filter(doctor=user).order_by('-appointment_date', 'appointment_time')
        elif user.role == 'admin':
            # Admins can see all appointments
            return Appointment.objects.all().order_by('-appointment_date', 'appointment_time')
        
        return Appointment.objects.none()
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/v1/appointments/
        Book a new appointment
        Room will be automatically assigned from doctor's room or department
        Only patients can book appointments lấy health_examintion_fee từ dept
        Service được doctor assign sau khi thăm khám
        """
        if request.user.role != 'patient':
            return Response({
                "success": False,
                "error": "Only patients can book appointments"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = serializer.validated_data['department']
        doctor = serializer.validated_data['doctor']
        
        # Chỉ tính phí thăm khám (health_examination_fee)
        # Service sẽ được doctor assign sau, lúc đó mới tính thêm service_fee
        health_examination_fee = department.health_examination_fee
        
        # Tự động gán room:
        # 1. Ưu tiên room của doctor (nếu doctor có room riêng)
        # 2. Nếu không, lấy room đầu tiên của department
        room = None
        try:
            doctor_profile = doctor.doctor_profile
            if hasattr(doctor_profile, 'room') and doctor_profile.room and doctor_profile.room.is_active:
                room = doctor_profile.room
            else:
                # Lấy room đầu tiên của department nếu doctor không có room riêng
                room = Room.objects.filter(
                    department=department,
                    is_active=True
                ).first()
        except Exception as e:
            # Fallback: lấy room đầu tiên của department
            room = Room.objects.filter(
                department=department,
                is_active=True
            ).first()
        
        # Create appointment WITHOUT service (service = None)
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            department=department,
            service=None,  # Service sẽ được doctor assign sau
            appointment_date=serializer.validated_data['appointment_date'],
            appointment_time=serializer.validated_data['appointment_time'],
            room=room,  # Tự động gán room
            symptoms=serializer.validated_data.get('symptoms'),
            reason=serializer.validated_data.get('reason'),
            notes=serializer.validated_data.get('notes'),
            estimated_fee=health_examination_fee,  # Chỉ tính phí thăm khám
            status='booked'
        )
        
        # Return full appointment data
        response_serializer = AppointmentSerializer(appointment)
        
        return Response({
            "success": True,
            "message": "Appointment booked successfully",
            "appointment": response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        operation_id="appointments_my_appointments",
        summary="Get current user's appointments with advanced filtering",
        description="""Retrieve appointments for the authenticated user with optional status and date range filtering.
        
        **Access Control:**
        - Available to all authenticated users (patients, doctors, admins)
        - Automatically filters based on user role (same as list endpoint)
        - Patients see their bookings, doctors see their schedule
        
        **Query Parameters (all optional):**
        
        1. **status** (string): Filter by appointment status
           - Values: `booked`, `confirmed`, `completed`, `cancelled`, `no_show`
           - Example: `?status=confirmed`
           - Use case: Show only upcoming confirmed appointments
        
        2. **date_from** (date): Start of date range
           - Format: YYYY-MM-DD
           - Example: `?date_from=2024-01-01`
           - Includes appointments on or after this date
        
        3. **date_to** (date): End of date range
           - Format: YYYY-MM-DD
           - Example: `?date_to=2024-12-31`
           - Includes appointments on or before this date
        
        4. **page** (integer): Pagination page number
           - Default: 1
           - Use with page_size for pagination
        
        **Filtering Combinations:**
        - Upcoming appointments: `?date_from=2024-01-15&status=confirmed`
        - Past appointments: `?date_to=2024-01-15&status=completed`
        - This month: `?date_from=2024-01-01&date_to=2024-01-31`
        - Cancelled history: `?status=cancelled`
        
        **Sorting:**
        - Results sorted by appointment_date (descending)
        - Then by appointment_time (descending)
        - Most recent appointments appear first
        
        **Response Structure:**
        Same as appointments list endpoint - complete appointment details with nested patient/doctor/department information.
        
        **Use Cases:**
        - Patient dashboard: "My Appointments" page
        - Doctor schedule: "My Schedule" filtered by date
        - Appointment history: Filter by status=completed
        - Upcoming visits: Filter by date_from=today, status!=cancelled
        - Cancellation tracking: Filter by status=cancelled
        
        **Best Practices:**
        - Combine status and date filters for specific views
        - Use date_from for "upcoming appointments" feature
        - Use status=completed for medical history
        - Cache frequently accessed date ranges
        
        **Difference from /appointments/:**
        - This endpoint: Role-based filtering built-in
        - Main list endpoint: Same filtering but more explicit in docs
        - Both return identical data structure
        - Use this for "My [Appointments/Schedule]" features
        """,
        tags=["Appointments"],
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by appointment status (booked, confirmed, completed, cancelled, no_show)',
                required=False,
            ),
            OpenApiParameter(
                name='date_from',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter appointments from this date (YYYY-MM-DD)',
                required=False,
            ),
            OpenApiParameter(
                name='date_to',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter appointments until this date (YYYY-MM-DD)',
                required=False,
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number',
                required=False,
            ),
        ],
        responses={
            200: AppointmentSerializer(many=True),
        }
    )
    @action(detail=False, methods=['get'], url_path='my-appointments')
    def my_appointments(self, request):
        """
        GET /api/v1/appointments/my-appointments/
        Get current user's appointments with filtering
        Query params: status, date_from, date_to, page
        """
        queryset = self.get_queryset()
        
        # Filter by status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__lte=date_to_obj)
            except ValueError:
                pass
        
        serializer = self.get_serializer(queryset, many=True) #serialize cho tất cả appointment
        return Response(serializer.data,
                     status=status.HTTP_200_OK)
    
    @extend_schema(
        operation_id="appointments_cancel",
        summary="Cancel appointment with 24-hour notice requirement",
        description="""Cancel an existing appointment with business rules enforcement.
        
        **Authorization & Permissions:**
        - **Patients**: Can cancel only their own appointments
        - **Doctors**: Can cancel appointments assigned to them
        - **Admins**: Can cancel any appointment
        - 403 error if user tries to cancel someone else's appointment
        
        **Cancellation Rules:**
        
        1. **24-Hour Minimum Notice:**
           - Must cancel at least 24 hours before appointment time
           - Example: Appointment at 2024-01-15 14:00 → Can cancel until 2024-01-14 14:00
           - Prevents last-minute cancellations
           - Returns 400 error if cancelled too late
        
        2. **Status Restrictions:**
           - Can only cancel appointments with status: `booked` or `confirmed`
           - Cannot cancel if already: `completed`, `cancelled`, `no_show`
           - Prevents double-cancellation
        
        3. **Past Appointments:**
           - Cannot cancel appointments in the past
           - Validates appointment_date against today
           - Returns 400 error for past dates
        
        **Required Field:**
        - `reason` (string): Explanation for cancellation
          - Required for tracking and analytics
          - Helps improve service quality
          - Examples: "Emergency came up", "Doctor's request", "Scheduling conflict"
        
        **Cancellation Process:**
        1. User requests cancellation with reason
        2. System validates 24-hour rule and current status
        3. Appointment status changed to `cancelled`
        4. Cancellation reason saved in appointment record
        5. Time slot becomes available for other patients
        6. (Future: Email notification sent to patient/doctor)
        
        **Response Data:**
        - Success confirmation message
        - Updated appointment object with status='cancelled'
        - Cancellation reason stored
        
        **Side Effects:**
        - Time slot released for rebooking
        - Room becomes available
        - Statistics updated (cancellation rate)
        - No refund processing (examination fee is consultation fee, not deposit)
        
        **Use Cases:**
        - Patient emergency: Cannot attend appointment
        - Doctor unavailability: Doctor cancels their schedule
        - Scheduling conflict: Patient needs to reschedule
        - Administrative cancellation: Hospital closure, system maintenance
        
        **Error Scenarios:**
        - 400: Too late (within 24 hours), already cancelled, past appointment
        - 403: Not your appointment (permission denied)
        - 404: Appointment doesn't exist
        
        **Best Practices:**
        - Always provide meaningful cancellation reason
        - Check cancellation deadline before showing cancel button
        - Offer reschedule option alongside cancel
        - Display 24-hour policy clearly to users
        
        **Note:**
        After cancellation, patients should use the booking endpoint to create a new appointment if they want to reschedule.
        """,
        tags=["Appointments"],
        request=AppointmentCancelSerializer,
        responses={
            200: {
                'description': 'Appointment cancelled successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Appointment cancelled successfully',
                            'appointment': {
                                'id': 1,
                                'status': 'cancelled',
                                'cancellation_reason': 'Changed my mind'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid request or business rule violation',
                'content': {
                    'application/json': {
                        'examples': {
                            'already_cancelled': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot cancel appointment with status: cancelled'
                                }
                            },
                            'too_late': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot cancel appointment within 24 hours of scheduled time'
                                }
                            },
                            'past_appointment': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot cancel an appointment that has already passed'
                                }
                            }
                        }
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'error': 'You can only cancel your own appointments'
                        }
                    }
                }
            },
            404: {
                'description': 'Appointment not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found.'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Cancel Appointment Example',
                value={
                    'reason': 'Changed my mind'
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        POST /api/v1/appointments/{id}/cancel/
        Cancel an appointment
        Business rule: Must cancel at least 24 hours before appointment
        - Patients can cancel their own appointments
        - Doctors can cancel their own appointments
        - Admins can cancel any appointment
        """
        appointment = self.get_object()
        
        # Check permissions based on role
        user_role = request.user.role
        
        if user_role == 'patient':
            # Patients can only cancel their own appointments
            if appointment.patient != request.user:
                return Response({
                    "success": False,
                    "error": "You can only cancel your own appointments"
                }, status=status.HTTP_403_FORBIDDEN)
        elif user_role == 'doctor':
            # Doctors can only cancel their own appointments
            if appointment.doctor != request.user:
                return Response({
                    "success": False,
                    "error": "You can only cancel your own appointments"
                }, status=status.HTTP_403_FORBIDDEN)
        elif user_role == 'admin':
            # Admins can cancel any appointment (no ownership check needed)
            pass
        else:
            # Reject any other roles
            return Response({
                "success": False,
                "error": "You do not have permission to cancel appointments"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if already cancelled or completed
        if appointment.status in ['cancelled', 'completed']:
            return Response({
                "success": False,
                "error": f"Cannot cancel appointment with status: {appointment.status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Business rule: Must cancel at least 24 hours before
        # Skip 24-hour rule for admins (they can cancel anytime)
        if user_role != 'admin':
            appointment_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )
            appointment_datetime = timezone.make_aware(appointment_datetime)
            time_until_appointment = appointment_datetime - timezone.now()
            
            # Check if appointment is in the past
            if time_until_appointment.total_seconds() < 0:
                return Response({
                    "success": False,
                    "error": "Cannot cancel an appointment that has already passed"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check 24-hour rule
            if time_until_appointment.total_seconds() < 24 * 3600:  # 24 hours in seconds
                return Response({
                    "success": False,
                    "error": "Cannot cancel appointment within 24 hours of scheduled time"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cancellation reason
        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cancellation_reason = serializer.validated_data.get('reason', '')
        
        # Update appointment
        appointment.status = 'cancelled'
        appointment.cancellation_reason = cancellation_reason
        appointment.cancelled_at = timezone.now()
        appointment.save()
        
        response_serializer = AppointmentSerializer(appointment)
        
        return Response({
            "success": True,
            "message": "Appointment cancelled successfully",
            "appointment": response_serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        operation_id="appointments_reschedule",
        summary="Reschedule appointment to new date and time",
        description="""Change appointment date/time while preserving all other details.
        
        **Authorization & Permissions:**
        - **Patients**: Can reschedule only their own appointments
        - **Doctors**: Can reschedule appointments assigned to them
        - **Admins**: Can reschedule any appointment
        - 403 error if trying to reschedule someone else's appointment
        
        **Rescheduling Rules:**
        
        1. **Status Restrictions:**
           - Can only reschedule appointments with status: `booked` or `confirmed`
           - Cannot reschedule if: `cancelled`, `completed`, `no_show`
           - Reason: Closed appointments shouldn't be modified
        
        2. **Slot Availability:**
           - New time slot must be available
           - Checks doctor's schedule for conflicts
           - Only considers `booked` and `confirmed` appointments
           - Returns 400 error with conflict message
        
        3. **Date/Time Validation:**
           - Same rules as booking: Cannot reschedule to past dates
           - Cannot reschedule more than 30 days in advance
           - Must be within operating hours (08:00-16:30)
        
        4. **Doctor Assignment:**
           - Cannot change doctor during reschedule
           - Use cancel + new booking to change doctor
           - Department remains the same
        
        **Required Fields:**
        - `new_date`: Target date (YYYY-MM-DD format)
        - `new_time`: Target time (HH:MM:SS format, e.g., "14:00:00")
        
        **Optional Fields:**
        - `reason`: Explanation for rescheduling (recommended)
          - Helps track patient behavior
          - Examples: "Work conflict", "Doctor's request", "Personal emergency"
          - Appended to appointment notes
        
        **Reschedule Process:**
        1. User provides new date, time, and optional reason
        2. System validates appointment status and permissions
        3. Check if new slot is available with same doctor
        4. Store original date/time in `rescheduled_from` field
        5. Update appointment_date and appointment_time
        6. Append reschedule reason to notes
        7. Reset status to `booked` (needs reconfirmation)
        8. Old time slot becomes available for others
        
        **Response Data:**
        - Success confirmation message
        - Updated appointment with new date/time
        - `rescheduled_from` object: Original date/time for history
        - All other appointment details remain unchanged
        
        **Rescheduled History:**
        The `rescheduled_from` field stores:
        ```json
        {
          "date": "2024-01-15",
          "time": "09:00"
        }
        ```
        Useful for tracking multiple reschedules and patient reliability.
        
        **Status Workflow After Reschedule:**
        - Status reset to `booked`
        - Requires staff confirmation again
        - Patient receives new confirmation (future feature)
        - Doctor notified of schedule change (future feature)
        
        **Use Cases:**
        - Patient time conflict: Need different slot same doctor
        - Doctor cancellation: Clinic offers alternative time
        - Emergency rescheduling: Patient can't make original time
        - Administrative adjustment: Fix scheduling errors
        
        **Difference from Cancel + Rebook:**
        - Reschedule: Preserves appointment ID, history, and notes
        - Cancel + Rebook: Creates new appointment, loses history
        - Reschedule: Better for tracking patient patterns
        - Use reschedule when keeping appointment ID matters
        
        **Error Scenarios:**
        - 400: Invalid status, slot taken, invalid date/time
        - 403: Not your appointment
        - 404: Appointment doesn't exist
        
        **Best Practices:**
        - Check available slots before showing reschedule form
        - Display rescheduling policy to users
        - Offer alternative slots on conflict error
        - Log reschedule history for analytics
        
        **Note:**
        If you need to change the doctor, cancel the current appointment and create a new booking.
        """,
        tags=["Appointments"],
        request=AppointmentRescheduleSerializer,
        responses={
            200: {
                'description': 'Appointment rescheduled successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Appointment rescheduled successfully',
                            'appointment': {
                                'id': 1,
                                'appointment_date': '2024-01-20',
                                'appointment_time': '10:00:00',
                                'status': 'booked',
                                'rescheduled_from': {
                                    'date': '2024-01-15',
                                    'time': '09:00:00'
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid request or business rule violation',
                'content': {
                    'application/json': {
                        'examples': {
                            'invalid_status': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot reschedule appointment with status: cancelled'
                                }
                            },
                            'slot_taken': {
                                'value': {
                                    'success': False,
                                    'error': 'New time slot is already taken. Please choose another time.',
                                    'suggestions': []
                                }
                            }
                        }
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'content': {
                    'application/json': {
                        'example': {
                            'success': False,
                            'error': 'You can only reschedule your own appointments'
                        }
                    }
                }
            },
            404: {
                'description': 'Appointment not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found.'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Reschedule Appointment Example',
                value={
                    'new_date': '2024-01-20',
                    'new_time': '10:00:00',
                    'reason': 'Need to change time'
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['put'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        """
        PUT /api/v1/appointments/{id}/reschedule/
        Reschedule an appointment
        """
        appointment = self.get_object()
        
        # Check ownership
        if request.user.role == 'patient' and appointment.patient != request.user:
            return Response({
                "success": False,
                "error": "You can only reschedule your own appointments"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if can be rescheduled
        if appointment.status in ['cancelled', 'completed', 'no_show']:
            return Response({
                "success": False,
                "error": f"Cannot reschedule appointment with status: {appointment.status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate reschedule data
        serializer = AppointmentRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_date = serializer.validated_data['new_date']
        new_time = serializer.validated_data['new_time']
        reason = serializer.validated_data.get('reason', '')
        
        # Check if new time slot is available: kiểm tra xem giờ còn trống ko
        conflicting_appointment = Appointment.objects.filter(
            doctor=appointment.doctor,
            appointment_date=new_date,
            appointment_time=new_time,
            status__in=['booked', 'confirmed']
        ).exclude(id=appointment.id).exists()
        
        if conflicting_appointment:
            return Response({
                "success": False,
                "error": "New time slot is already taken. Please choose another time.",
                "suggestions": []  # Could add logic to suggest alternative slots
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store old date/time
        old_date_time = {
            "date": appointment.appointment_date.strftime('%Y-%m-%d'),
            "time": appointment.appointment_time.strftime('%H:%M')
        }
        
        # Update appointment
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.rescheduled_from = old_date_time
        appointment.notes = f"{appointment.notes or ''}\nRescheduled: {reason}".strip()
        appointment.status = 'booked'  # Reset to booked status
        appointment.save()
        
        response_serializer = AppointmentSerializer(appointment)
        
        return Response({
            "success": True,
            "message": "Appointment rescheduled successfully",
            "appointment": response_serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="appointments_assign_service",
        summary="Doctor assigns medical service to appointment",
        description="""Allow doctors to assign additional medical services during/after consultation.
        
        **Authorization & Permissions:**
        - **Only doctors** can assign services (403 error for patients/admins)
        - Doctor can only assign to **their own appointments**
        - Cannot assign to appointments of other doctors
        
        **Service Assignment Business Logic:**
        
        **When to Assign Services:**
        - During consultation: Doctor determines patient needs X-Ray, blood test, etc.
        - After examination: Based on diagnosis
        - Service adds to the total fee
        
        **Initial Booking vs Service Assignment:**
        1. **Initial Booking**: Patient pays `health_examination_fee` (consultation fee from department)
        2. **After Consultation**: Doctor assigns services (X-Ray, CT Scan, lab tests, etc.)
        3. **Final Fee**: `estimated_fee` = health_examination_fee + service_fee
        
        **Status Requirements:**
        - Can only assign to: `confirmed` or `completed` appointments
        - Cannot assign to: `booked`, `cancelled`, `no_show`
        - Reason: Services assigned during/after actual visit
        
        **Department Matching:**
        - Service must belong to appointment's department
        - Ensures service is relevant to doctor's specialty
        - Example: Cardiology doctor assigns Cardiology services only
        - Returns 400 error if department mismatch
        
        **Required Field:**
        - `service_id`: ID of the service to assign
        
        **Validation Rules:**
        1. Appointment exists and accessible
        2. User is a doctor (not patient/admin)
        3. Doctor owns the appointment
        4. Appointment status is confirmed or completed
        5. Service exists and is active
        6. Service belongs to appointment's department
        
        **Assignment Process:**
        1. Doctor views patient during appointment
        2. Doctor determines needed service (e.g., blood test)
        3. POST to assign-service with service_id
        4. System validates all rules
        5. Service assigned to appointment
        6. estimated_fee updated: base_fee + service_fee
        7. Fee breakdown returned in response
        
        **Fee Calculation:**
        - **health_examination_fee**: Base consultation fee (from department)
        - **service_fee**: Price of assigned service (from service model)
        - **total_fee**: health_examination_fee + service_fee
        
        **Response Data:**
        - Success confirmation
        - Updated appointment with assigned service
        - Fee breakdown showing:
          - health_examination_fee (base)
          - service_fee (added)
          - total_fee (sum)
        
        **Use Cases:**
        - Doctor orders lab test during checkup
        - Cardiologist requests ECG for patient
        - Orthopedist orders X-Ray
        - General practitioner assigns blood work
        
        **Service Examples:**
        - X-Ray Imaging
        - Blood Test (Complete Blood Count)
        - ECG (Electrocardiogram)
        - CT Scan
        - Ultrasound
        - Laboratory Analysis
        
        **Multiple Services:**
        Currently supports one service per appointment. For multiple services:
        - Call endpoint multiple times (each service separately), OR
        - Future enhancement: Accept array of service_ids
        
        **Error Scenarios:**
        - 400: Missing service_id, wrong status, department mismatch
        - 403: Not a doctor, not your appointment
        - 404: Appointment or service not found
        
        **Best Practices:**
        - Assign services during consultation, not before
        - Verify service is appropriate for department
        - Explain fee increase to patient
        - Document service reason in medical record
        
        **Financial Flow:**
        1. Patient books: Pays/owes health_examination_fee
        2. Doctor assigns service: Fee increases by service_fee
        3. Patient completes payment: Total = examination + service
        
        **Note:**
        Service assignment does NOT create medical record automatically. Use the create_medical_record endpoint after completing examination.
        """,
        tags=["Appointments"],
        request=AppointmentAssignServiceSerializer,
        responses={
            200: {
                'description': 'Service assigned successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Service assigned successfully',
                            'appointment': {
                                'id': 1,
                                'service': {
                                    'id': 1,
                                    'name': 'X-Ray',
                                    'price': '200000.00'
                                },
                                'estimated_fee': '700000.00'
                            },
                            'fee_breakdown': {
                                'health_examination_fee': '500000.00',
                                'service_fee': '200000.00',
                                'total_fee': '700000.00'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid request or business rule violation',
                'content': {
                    'application/json': {
                        'examples': {
                            'missing_service_id': {
                                'value': {
                                    'success': False,
                                    'error': 'service_id is required'
                                }
                            },
                            'invalid_status': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot assign service to appointment with status: booked'
                                }
                            },
                            'wrong_department': {
                                'value': {
                                    'success': False,
                                    'error': "Service does not belong to the appointment's department"
                                }
                            }
                        }
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'content': {
                    'application/json': {
                        'examples': {
                            'not_doctor': {
                                'value': {
                                    'success': False,
                                    'error': 'Only doctors can assign services to appointments'
                                }
                            },
                            'not_owner': {
                                'value': {
                                    'success': False,
                                    'error': 'You can only assign service to your own appointments'
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Appointment or service not found',
                'content': {
                    'application/json': {
                        'examples': {
                            'appointment_not_found': {
                                'value': {
                                    'detail': 'Not found.'
                                }
                            },
                            'service_not_found': {
                                'value': {
                                    'success': False,
                                    'error': 'Service not found or inactive'
                                }
                            }
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Assign Service Example',
                value={
                    'service_id': 1
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='assign-service')
    def assign_service(self, request, pk=None):
        """
        POST /api/v1/appointments/{id}/assign-service/
        Assign a service to an appointment
        Only the doctor of the appointment can assign services
        """
        appointment = self.get_object()
        
        # Only doctors can assign services
        if request.user.role != 'doctor':
            return Response({
                "success": False,
                "error": "Only doctors can assign services to appointments"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check ownership - only the doctor of this appointment can assign service
        if appointment.doctor != request.user:
            return Response({
                "success": False,
                "error": "You can only assign service to your own appointments"
            }, status=status.HTTP_403_FORBIDDEN)
            
        if appointment.status not in ["confirmed", "completed"]:
            return Response({
                "success": False,
                "error": f"Cannot assign service to appointment with status: {appointment.status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #Validate service_id
        service_id = request.data.get('service_id')
        if not service_id:
            return Response({
                "success": False,
                "error": "service_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return Response({
                "success": False,
                "error": "Service not found or inactive"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if service belongs to the same department
        if service.department != appointment.department:
            return Response({
                "success": False,
                "error": "Service does not belong to the appointment's department"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update appointment: assign service và tính lại phí
        appointment.service = service
        
        health_examination_fee = appointment.department.health_examination_fee
        service_fee = service.price
        appointment.estimated_fee = health_examination_fee + service_fee
        appointment.save()
        
        response_serializer = AppointmentSerializer(appointment)
        
        return Response({
            "success": True,
            "message": "Service assigned successfully",
            "appointment": response_serializer.data,
            "fee_breakdown": {
                "health_examination_fee": str(health_examination_fee),
                "service_fee": str(service_fee),
                "total_fee": str(appointment.estimated_fee)
            }
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        operation_id="appointments_create_medical_record",
        summary="Create or update medical record after consultation",
        description="""Create detailed medical record documenting diagnosis, prescription, and treatment plan.
        
        **Authorization & Permissions:**
        - **Only doctors** can create/update medical records
        - Doctor must be assigned to the appointment
        - Cannot create records for other doctors' appointments
        
        **Medical Record Purpose:**
        Documents complete consultation including:
        - Patient's diagnosis
        - Prescribed medications
        - Treatment recommendations
        - Vital signs measurements
        - Doctor's clinical notes
        - Follow-up scheduling
        
        **When to Create Medical Record:**
        - After completing patient examination
        - During consultation (real-time documentation)
        - When appointment status is `confirmed` or `completed`
        - Cannot create for `booked`, `cancelled`, or `no_show` appointments
        
        **Status Requirements:**
        - `confirmed`: Appointment happening now, can document
        - `completed`: Consultation finished, finalizing record
        - Other statuses: 400 error (record requires actual visit)
        
        **Create vs Update Behavior:**
        - **POST**: Creates new record if none exists, updates if exists (idempotent)
        - **PUT**: Same as POST (both methods supported)
        - One medical record per appointment (enforced by database)
        - Existing records: Updates all fields, partial update allowed
        
        **Required Fields:**
        - `diagnosis`: Medical diagnosis (e.g., "Acute bronchitis", "Type 2 Diabetes")
        - `prescription`: Medication details with dosage and duration
          - Format: "Drug name dose, frequency, duration"
          - Example: "Amoxicillin 500mg, 3 times daily for 7 days"
        - `treatment_plan`: Recommended actions and lifestyle advice
          - Example: "Rest for 3 days, avoid cold drinks, increase fluid intake"
        
        **Optional Fields:**
        - `notes`: Additional clinical observations
          - Doctor's private notes
          - Patient behavior/compliance notes
          - Risk factors or concerns
        
        - `follow_up_date`: Date for next visit (YYYY-MM-DD)
          - Used for chronic conditions
          - Post-surgery checkups
          - Monitoring treatment progress
        
        - `vital_signs`: JSON object with measurements
          - blood_pressure: "120/80" (mmHg)
          - temperature: "37.2" (°C)
          - heart_rate: "72" (bpm)
          - respiratory_rate: "18" (breaths/min)
          - oxygen_saturation: "98" (%)
          - weight: "70" (kg)
          - height: "175" (cm)
        
        **Vital Signs Format:**
        ```json
        {
          "blood_pressure": "120/80",
          "temperature": "37.2",
          "heart_rate": "72",
          "respiratory_rate": "18",
          "oxygen_saturation": "98",
          "weight": "70.5",
          "height": "175"
        }
        ```
        
        **Medical Record Creation Process:**
        1. Doctor completes patient examination
        2. Doctor documents findings in system
        3. POST to /appointments/{id}/medical-record/
        4. System validates doctor ownership and status
        5. Creates MedicalRecord linked to appointment
        6. Stores created_by (doctor's user ID)
        7. Timestamps: created_at and updated_at
        8. Returns complete medical record data
        
        **Updating Existing Record:**
        1. Medical record already exists for appointment
        2. Doctor submits updated data (POST or PUT)
        3. System updates existing record (no duplicate)
        4. Updates updated_at timestamp
        5. created_by remains unchanged
        6. Returns updated medical record
        
        **Response Data:**
        - Success confirmation (created or updated)
        - Complete medical record including:
          - id: Medical record ID
          - appointment: Appointment ID
          - diagnosis, prescription, treatment_plan
          - notes, follow_up_date
          - vital_signs (JSON object)
          - created_by: Doctor's user ID
          - created_by_name: Doctor's full name
          - created_at, updated_at timestamps
        
        **Use Cases:**
        - General consultation: Diagnosis + prescription
        - Chronic disease management: Treatment plan + follow-up
        - Emergency visit: Vital signs + immediate treatment
        - Routine checkup: Vital signs documentation
        - Specialist consultation: Detailed diagnosis + referral notes
        
        **Integration with Appointment:**
        - Medical record links to appointment (one-to-one)
        - Can access via appointment.medical_record
        - Appointment status often changed to `completed` after record creation
        - Medical record ID stored in appointment response
        
        **Privacy & Security:**
        - Only assigned doctor can create/view/update
        - Patient can view their own medical records
        - Admins can view all records (audit trail)
        - Contains sensitive health information (HIPAA/GDPR compliance)
        
        **Best Practices:**
        - Create record immediately after consultation
        - Include comprehensive vital signs when available
        - Be specific in diagnosis (use medical terminology)
        - Prescription: Include dosage, frequency, duration
        - Treatment plan: Actionable, clear instructions
        - Follow-up date: Set for chronic conditions or monitoring
        - Notes: Document anything unusual or important
        
        **Error Scenarios:**
        - 400: Invalid status, validation errors (vital_signs format)
        - 403: Not a doctor, not your appointment
        - 404: Appointment doesn't exist
        
        **Validation Rules:**
        - vital_signs must be valid JSON object (if provided)
        - follow_up_date must be future date
        - diagnosis, prescription, treatment_plan cannot be empty
        
        **Common Prescription Format:**
        ```
        1. Paracetamol 500mg - 2 tablets every 6 hours for 3 days
        2. Amoxicillin 500mg - 1 capsule 3 times daily for 7 days
        3. Cetirizine 10mg - 1 tablet before bed for 5 days
        ```
        
        **Status Code Logic:**
        - 201 Created: New medical record created
        - 200 OK: Existing medical record updated
        
        **Note:**
        After creating medical record, consider changing appointment status to `completed` using a separate endpoint (future feature).
        """,
        tags=["Appointments"],
        request=MedicalRecordCreateUpdateSerializer,
        responses={
            200: {
                'description': 'Medical record created/updated successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Medical record created successfully',
                            'medical_record': {
                                'id': 1,
                                'appointment': 1,
                                'diagnosis': 'Common cold',
                                'prescription': 'Paracetamol 500mg, 2 tablets every 6 hours',
                                'treatment_plan': 'Rest and drink plenty of fluids',
                                'notes': 'Patient should return if symptoms persist',
                                'follow_up_date': '2024-01-20',
                                'vital_signs': {
                                    'blood_pressure': '120/80',
                                    'temperature': '37.2',
                                    'heart_rate': '72'
                                },
                                'created_by': 2,
                                'created_by_name': 'Dr. Jane Smith',
                                'created_at': '2024-01-15T10:30:00Z',
                                'updated_at': '2024-01-15T10:30:00Z'
                            }
                        }
                    }
                }
            },
            201: {
                'description': 'Medical record created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True,
                            'message': 'Medical record created successfully',
                            'medical_record': {
                                'id': 1,
                                'appointment': 1,
                                'diagnosis': 'Common cold',
                                'prescription': 'Paracetamol 500mg, 2 tablets every 6 hours',
                                'treatment_plan': 'Rest and drink plenty of fluids',
                                'notes': 'Patient should return if symptoms persist',
                                'follow_up_date': '2024-01-20',
                                'vital_signs': {
                                    'blood_pressure': '120/80',
                                    'temperature': '37.2',
                                    'heart_rate': '72'
                                },
                                'created_by': 2,
                                'created_by_name': 'Dr. Jane Smith',
                                'created_at': '2024-01-15T10:30:00Z',
                                'updated_at': '2024-01-15T10:30:00Z'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid request or business rule violation',
                'content': {
                    'application/json': {
                        'examples': {
                            'invalid_status': {
                                'value': {
                                    'success': False,
                                    'error': 'Cannot create medical record for appointment with status: booked'
                                }
                            },
                            'validation_error': {
                                'value': {
                                    'vital_signs': ['Vital signs must be a JSON object']
                                }
                            }
                        }
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'content': {
                    'application/json': {
                        'examples': {
                            'not_doctor': {
                                'value': {
                                    'success': False,
                                    'error': 'Only doctors can create medical records'
                                }
                            },
                            'not_owner': {
                                'value': {
                                    'success': False,
                                    'error': 'You can only create medical records for your own appointments'
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Appointment not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Not found.'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Create Medical Record Example',
                value={
                    'diagnosis': 'Common cold',
                    'prescription': 'Paracetamol 500mg, 2 tablets every 6 hours for 3 days',
                    'treatment_plan': 'Rest and drink plenty of fluids. Avoid cold drinks.',
                    'notes': 'Patient should return if symptoms persist after 3 days',
                    'follow_up_date': '2024-01-20',
                    'vital_signs': {
                        'blood_pressure': '120/80',
                        'temperature': '37.2',
                        'heart_rate': '72',
                        'respiratory_rate': '18'
                    }
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['post', 'put'], url_path='medical-record')
    def create_medical_record(self, request, pk=None):
        """
        POST/PUT /api/v1/appointments/{id}/medical-record/
        Create or update a medical record for an appointment
        Only the doctor assigned to the appointment can create/update medical records
        """
        appointment = self.get_object()
        
        # Only doctors can create medical records
        if request.user.role != 'doctor':
            return Response({
                "success": False,
                "error": "Only doctors can create medical records"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check ownership - only the doctor of this appointment can create medical record
        if appointment.doctor != request.user:
            return Response({
                "success": False,
                "error": "You can only create medical records for your own appointments"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Only allow medical record for confirmed or completed appointments
        if appointment.status not in ["confirmed", "completed"]:
            return Response({
                "success": False,
                "error": f"Cannot create medical record for appointment with status: {appointment.status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if medical record already exists
        medical_record, created = MedicalRecord.objects.get_or_create(
            appointment=appointment,
            defaults={'created_by': request.user}
        )
        
        # If updating existing record, update created_by if not set
        if not created and not medical_record.created_by:
            medical_record.created_by = request.user
        
        # Validate and save data
        serializer = MedicalRecordCreateUpdateSerializer(
            medical_record,
            data=request.data,
            partial=not created  # Allow partial update if record exists
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Refresh from DB to get updated data
            medical_record.refresh_from_db()
            response_serializer = MedicalRecordSerializer(medical_record)
            
            return Response({
                "success": True,
                "message": "Medical record created successfully" if created else "Medical record updated successfully",
                "medical_record": response_serializer.data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)