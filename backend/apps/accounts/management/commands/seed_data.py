from django.core.management.base import BaseCommand
from apps.accounts.models import User, Patient, Doctor
from datetime import date

class Command(BaseCommand):
    help = "Seed database with sample data"
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        
        admin, created = User.objects.get_or_create(
            email="admin@mỵheathcare.com",
            defaults={
                "full_name": "Admin User",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        doctors_data = [
            {
                'email': 'doctor1@clinic.com',
                'full_name': 'BS. Nguyễn Văn A',
                'phone_num': '0901111111',
                'title': 'Bác sĩ',
                'specialization': 'Nội khoa',
                'license_number': 'BS001',
                'experience_years': 5,
                'consultation_fee': 200000
            },
            {
                'email': 'doctor2@clinic.com',
                'full_name': 'ThS. BS. Trần Thị B',
                'phone_num': '0901111112',
                'title': 'Thạc sĩ, Bác sĩ',
                'specialization': 'Tim mạch',
                'license_number': 'BS002',
                'experience_years': 8,
                'consultation_fee': 300000
            },
            {
                'email': 'doctor3@clinic.com',
                'full_name': 'TS. BS. Lê Văn C',
                'phone_num': '0901111113',
                'title': 'Tiến sĩ, Bác sĩ',
                'specialization': 'Da liễu',
                'license_number': 'BS003',
                'experience_years': 10,
                'consultation_fee': 350000
            },
        ]
        
        for data in doctors_data:
            user, created = User.objects.get_or_create(
                email = data["email"],
                defaults={
                    "full_name": data["full_name"],
                    "role": "doctor",
                    "phone_num": data["phone_num"],
                }
            )
            if created:
                user.set_password("doctor123")
                user.save()
                
                Doctor.objects.create(
                    user=user,
                    title=data['title'],
                    specialization=data['specialization'],
                    license_number=data['license_number'],
                    experience_years=data['experience_years'],
                    consultation_fee=data['consultation_fee']
                )
                self.stdout.write(self.style.SUCCESS(f'Created doctor user: {data["full_name"]}'))
                
        patients_data = [
            {
                'email': 'patient1@example.com',
                'full_name': 'Nguyễn Thị D',
                'phone_num': '0902222221',
                'date_of_birth': date(1990, 1, 15),
                'gender': 'female',
                'insurance_id': 'INS123456',
                'address': '123 Nguyễn Huệ, Q1, TPHCM',
                'emergency_contact': 'Trần Văn X',
                'emergency_contact_phone': '0903333333'
            },
            {
                'email': 'patient2@example.com',
                'full_name': 'Trần Văn E',
                'phone_num': '0902222222',
                'date_of_birth': date(1985, 5, 20),
                'insurance_id': 'INS654321',
                'gender': 'male',
                'address': '456 Lê Lợi, Q3, TPHCM',
                'emergency_contact': 'Lê Thị Y',
                'emergency_contact_phone': '0904444444'
            },
            {
                'email': 'patient3@example.com',
                'full_name': 'Phạm Thị F',
                'phone_num': '0902222223',
                'date_of_birth': date(1992, 8, 10),
                'insurance_id': 'INS112233',
                'gender': 'female',
                'address': '789 Trần Hưng Đạo, Q5, TPHCM',
                'emergency_contact': 'Ngô Văn Z',
                'emergency_contact_phone': '0905555555'
            }, 
        ]
        
        for data in patients_data:
            user, created = User.objects.get_or_create(
                email = data["email"],
                defaults={
                    "full_name": data["full_name"],
                    "role": "patient",
                    "phone_num": data["phone_num"],
                }
            )
            if created:
                user.set_password("patient123")
                user.save()
                
                Patient.objects.create(
                    user=user,
                    date_of_birth=data['date_of_birth'],
                    gender=data["gender"],
                    address=data['address'],
                    insurance_id=data['insurance_id'],
                    emergency_contact=data['emergency_contact'],
                    emergency_contact_phone=data['emergency_contact_phone']
                )
        self.stdout.write(self.style.SUCCESS(f'Created patient user: {data["full_name"] }'))
        self.stdout.write(self.style.SUCCESS('\n✓ Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('\nAccounts created:'))
        self.stdout.write('  Admin: admin@clinic.com / admin123')
        self.stdout.write('  Doctor: doctor1@clinic.com / doctor123')
        self.stdout.write('  Patient: patient1@example.com / patient123')