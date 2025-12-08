from django.contrib.auth import get_user_model
from apps.accounts.models import Doctor
from apps.appointments.models import Department, Appointment, MedicalRecord
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

# Create test patient (or get if exists)
patient, created = User.objects.get_or_create(
    email='patient1@test.com',
    defaults={
        'password': 'password123',
        'full_name': 'Patient One',
        'role': 'patient',
        'phone_num': '+84901234567'
    }
)

# Create test doctor (or get if exists)
doctor_user, created = User.objects.get_or_create(
    email='doctor1@test.com',
    defaults={
        'password': 'password123',
        'full_name': 'Dr. Smith',
        'role': 'doctor',
        'phone_num': '+84987654321'
    }
)

# Create department (or get if exists)
dept, created = Department.objects.get_or_create(
    name='Cardiology',
    defaults={
        'icon': 'heart',
        'health_examination_fee': Decimal('500000.00')
    }
)

# Create doctor profile (or get if exists)
doctor, created = Doctor.objects.get_or_create(
    user=doctor_user,
    defaults={
        'department': dept,
        'title': 'MD',
        'specialization': 'Heart Specialist'
    }
)

# Create appointment (or get if exists)
tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
appt, created = Appointment.objects.get_or_create(
    patient=patient,
    doctor=doctor_user,
    appointment_date=tomorrow,
    appointment_time='09:00',
    defaults={
        'department': dept,
        'symptoms': 'Chest pain',
        'status': 'completed'
    }
)

# Create medical record (or get if exists)
med_record, created = MedicalRecord.objects.get_or_create(
    appointment=appt,
    defaults={
        'diagnosis': 'Heartburn',
        'prescription': 'Antacids 2x daily',
        'treatment_plan': 'Rest and medication',
        'notes': 'Patient should rest',
        'created_by': doctor_user,
        'vital_signs': {'blood_pressure': '120/80', 'heart_rate': 72}
    }
)

print("✓ Patient:", patient.full_name, f"(ID: {patient.id})")
print("✓ Doctor:", doctor_user.full_name, f"(ID: {doctor_user.id})")
print("✓ Department:", dept.name, f"(ID: {dept.id})")
print("✓ Appointment:", appt.id, f"- {appt.appointment_date} at {appt.appointment_time}")
print("✓ Medical Record:", med_record.id)
print("\nTest credentials:")
print("  Patient: patient1@test.com / password123")
print("  Doctor: doctor1@test.com / password123")

