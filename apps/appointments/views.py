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

from .models import Department, Service, Room, Appointment, Department
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
    DepartmentDetailSerializer
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
        summary="List all departments",
        description="Get a paginated list of all active departments",
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
        summary="Retrieve department details",
        description="Get detailed information about a specific department including services and doctors",
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
        summary="List all services",
        description="Get a list of all active services, optionally filtered by department_id or specialty_id",
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
        summary="Retrieve service details",
        description="Get detailed information about a specific service",
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
        summary="Get available appointment slots",
        description="Get available time slots for a doctor on a specific date. Returns all time slots (08:00-16:30) with availability status.",
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
        return AppointmentSerializer
    
    @extend_schema(
        operation_id="appointments_create",
        summary="Book a new appointment",
        description="Create a new appointment. Only patients can book appointments. Room will be automatically assigned from doctor's room or department.",
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
        summary="List appointments",
        description="Get a list of appointments. Patients see only their appointments, doctors see their appointments, admins see all appointments.",
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
        summary="Retrieve appointment details",
        description="Get detailed information about a specific appointment",
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
        summary="Get doctors by department",
        description="Get list of doctors filtered by department_id. Useful for dynamically loading doctors when department is selected.",
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
        summary="Get my appointments",
        description="Get current user's appointments with optional filtering by status and date range",
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
        summary="Cancel an appointment",
        description="Cancel an appointment. Must cancel at least 24 hours before appointment. Patients can cancel their own appointments, doctors can cancel their own appointments, admins can cancel any appointment.",
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
        summary="Reschedule an appointment",
        description="Reschedule an appointment to a new date and time. Patients can reschedule their own appointments. The new time slot must be available.",
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
        summary="Assign service to appointment",
        description="Assign a service to an appointment. Only the doctor of the appointment can assign services. The appointment must be in 'confirmed' or 'completed' status. The service must belong to the same department as the appointment.",
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