from django.core.management.base import BaseCommand
from apps.accounts.models import User, Patient, Doctor
from apps.appointments.models import Department
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
            # Nhi khoa - 3 doctors
            {
                'email': 'doctor.nhi1@clinic.com',
                'full_name': 'BS. Nguyễn Thị Lan',
                'phone_num': '0901111001',
                'title': 'Bác sĩ',
                'specialization': 'Nhi khoa',
                'department_name': 'Nhi khoa',
                'license_number': 'BS001',
                'experience_years': 5,
                'consultation_fee': 200000,
                'rating': 4.5,
                'total_reviews': 25,
                'bio': 'Bác sĩ chuyên khoa Nhi với 5 năm kinh nghiệm, chuyên khám và điều trị các bệnh thường gặp ở trẻ em.'
            },
            {
                'email': 'doctor.nhi2@clinic.com',
                'full_name': 'ThS. BS. Trần Văn Minh',
                'phone_num': '0901111002',
                'title': 'Thạc sĩ, Bác sĩ',
                'specialization': 'Nhi khoa',
                'department_name': 'Nhi khoa',
                'license_number': 'BS002',
                'experience_years': 8,
                'consultation_fee': 250000,
                'rating': 4.8,
                'total_reviews': 42,
                'bio': 'Thạc sĩ, Bác sĩ chuyên khoa Nhi với 8 năm kinh nghiệm, chuyên về tiêm chủng và dinh dưỡng trẻ em.'
            },
            {
                'email': 'doctor.nhi3@clinic.com',
                'full_name': 'TS. BS. Lê Thị Hoa',
                'phone_num': '0901111003',
                'title': 'Tiến sĩ, Bác sĩ',
                'specialization': 'Nhi khoa',
                'department_name': 'Nhi khoa',
                'license_number': 'BS003',
                'experience_years': 12,
                'consultation_fee': 300000,
                'rating': 4.9,
                'total_reviews': 68,
                'bio': 'Tiến sĩ, Bác sĩ chuyên khoa Nhi với 12 năm kinh nghiệm, chuyên về các bệnh lý phức tạp ở trẻ em.'
            },
            # Tim mạch - 4 doctors
            {
                'email': 'doctor.tim1@clinic.com',
                'full_name': 'BS. Phạm Văn Đức',
                'phone_num': '0901112001',
                'title': 'Bác sĩ',
                'specialization': 'Tim mạch',
                'department_name': 'Tim mạch',
                'license_number': 'BS004',
                'experience_years': 6,
                'consultation_fee': 300000,
                'rating': 4.6,
                'total_reviews': 30,
                'bio': 'Bác sĩ chuyên khoa Tim mạch với 6 năm kinh nghiệm, chuyên khám và điều trị các bệnh tim mạch thường gặp.'
            },
            {
                'email': 'doctor.tim2@clinic.com',
                'full_name': 'ThS. BS. Hoàng Thị Mai',
                'phone_num': '0901112002',
                'title': 'Thạc sĩ, Bác sĩ',
                'specialization': 'Tim mạch',
                'department_name': 'Tim mạch',
                'license_number': 'BS005',
                'experience_years': 9,
                'consultation_fee': 350000,
                'rating': 4.7,
                'total_reviews': 45,
                'bio': 'Thạc sĩ, Bác sĩ chuyên khoa Tim mạch với 9 năm kinh nghiệm, chuyên về siêu âm tim và điện tâm đồ.'
            },
            {
                'email': 'doctor.tim3@clinic.com',
                'full_name': 'TS. BS. Vũ Văn Hùng',
                'phone_num': '0901112003',
                'title': 'Tiến sĩ, Bác sĩ',
                'specialization': 'Tim mạch',
                'department_name': 'Tim mạch',
                'license_number': 'BS006',
                'experience_years': 15,
                'consultation_fee': 400000,
                'rating': 4.9,
                'total_reviews': 85,
                'bio': 'Tiến sĩ, Bác sĩ chuyên khoa Tim mạch với 15 năm kinh nghiệm, chuyên về can thiệp tim mạch và phẫu thuật tim.'
            },
            {
                'email': 'doctor.tim4@clinic.com',
                'full_name': 'BS. Đỗ Thị Linh',
                'phone_num': '0901112004',
                'title': 'Bác sĩ',
                'specialization': 'Tim mạch',
                'department_name': 'Tim mạch',
                'license_number': 'BS007',
                'experience_years': 4,
                'consultation_fee': 280000,
                'rating': 4.4,
                'total_reviews': 18,
                'bio': 'Bác sĩ chuyên khoa Tim mạch với 4 năm kinh nghiệm, chuyên khám và tư vấn sức khỏe tim mạch.'
            },
            # Nội tiết - 3 doctors
            {
                'email': 'doctor.noi1@clinic.com',
                'full_name': 'BS. Nguyễn Văn An',
                'phone_num': '0901113001',
                'title': 'Bác sĩ',
                'specialization': 'Nội tiết',
                'department_name': 'Nội tiết',
                'license_number': 'BS008',
                'experience_years': 5,
                'consultation_fee': 250000,
                'rating': 4.5,
                'total_reviews': 22,
                'bio': 'Bác sĩ chuyên khoa Nội tiết với 5 năm kinh nghiệm, chuyên điều trị đái tháo đường và các rối loạn nội tiết.'
            },
            {
                'email': 'doctor.noi2@clinic.com',
                'full_name': 'ThS. BS. Trần Thị Hương',
                'phone_num': '0901113002',
                'title': 'Thạc sĩ, Bác sĩ',
                'specialization': 'Nội tiết',
                'department_name': 'Nội tiết',
                'license_number': 'BS009',
                'experience_years': 8,
                'consultation_fee': 300000,
                'rating': 4.7,
                'total_reviews': 38,
                'bio': 'Thạc sĩ, Bác sĩ chuyên khoa Nội tiết với 8 năm kinh nghiệm, chuyên về xét nghiệm hormone và dinh dưỡng.'
            },
            {
                'email': 'doctor.noi3@clinic.com',
                'full_name': 'TS. BS. Lê Văn Tuấn',
                'phone_num': '0901113003',
                'title': 'Tiến sĩ, Bác sĩ',
                'specialization': 'Nội tiết',
                'department_name': 'Nội tiết',
                'license_number': 'BS010',
                'experience_years': 11,
                'consultation_fee': 350000,
                'rating': 4.8,
                'total_reviews': 55,
                'bio': 'Tiến sĩ, Bác sĩ chuyên khoa Nội tiết với 11 năm kinh nghiệm, chuyên về các bệnh lý nội tiết phức tạp.'
            },
            # Da liễu - 3 doctors
            {
                'email': 'doctor.da1@clinic.com',
                'full_name': 'BS. Phạm Thị Hoa',
                'phone_num': '0901114001',
                'title': 'Bác sĩ',
                'specialization': 'Da liễu',
                'department_name': 'Da liễu',
                'license_number': 'BS011',
                'experience_years': 6,
                'consultation_fee': 200000,
                'rating': 4.6,
                'total_reviews': 28,
                'bio': 'Bác sĩ chuyên khoa Da liễu với 6 năm kinh nghiệm, chuyên điều trị mụn và các bệnh da thường gặp.'
            },
            {
                'email': 'doctor.da2@clinic.com',
                'full_name': 'ThS. BS. Hoàng Văn Nam',
                'phone_num': '0901114002',
                'title': 'Thạc sĩ, Bác sĩ',
                'specialization': 'Da liễu',
                'department_name': 'Da liễu',
                'license_number': 'BS012',
                'experience_years': 9,
                'consultation_fee': 250000,
                'rating': 4.7,
                'total_reviews': 40,
                'bio': 'Thạc sĩ, Bác sĩ chuyên khoa Da liễu với 9 năm kinh nghiệm, chuyên về điều trị nám, tàn nhang và thẩm mỹ da.'
            },
            {
                'email': 'doctor.da3@clinic.com',
                'full_name': 'TS. BS. Vũ Thị Lan',
                'phone_num': '0901114003',
                'title': 'Tiến sĩ, Bác sĩ',
                'specialization': 'Da liễu',
                'department_name': 'Da liễu',
                'license_number': 'BS013',
                'experience_years': 13,
                'consultation_fee': 300000,
                'rating': 4.9,
                'total_reviews': 72,
                'bio': 'Tiến sĩ, Bác sĩ chuyên khoa Da liễu với 13 năm kinh nghiệm, chuyên về các bệnh da phức tạp và ung thư da.'
            },
            # Sản phụ khoa - 3 doctors
            {
                'email': 'doctor.san1@clinic.com',
                'full_name': 'BS. Đỗ Thị Mai',
                'phone_num': '0901115001',
                'title': 'Bác sĩ',
                'specialization': 'Sản phụ khoa',
                'department_name': 'Sản phụ khoa',
                'license_number': 'BS014',
                'experience_years': 5,
                'consultation_fee': 250000,
                'rating': 4.5,
                'total_reviews': 24,
                'bio': 'Bác sĩ chuyên khoa Sản phụ khoa với 5 năm kinh nghiệm, chuyên khám thai và chăm sóc sức khỏe phụ nữ.'
            },
            {
                'email': 'doctor.san2@clinic.com',
                'full_name': 'ThS. BS. Nguyễn Văn Hải',
                'phone_num': '0901115002',
                'title': 'Thạc sĩ, Bác sĩ',
                'specialization': 'Sản phụ khoa',
                'department_name': 'Sản phụ khoa',
                'license_number': 'BS015',
                'experience_years': 8,
                'consultation_fee': 300000,
                'rating': 4.7,
                'total_reviews': 36,
                'bio': 'Thạc sĩ, Bác sĩ chuyên khoa Sản phụ khoa với 8 năm kinh nghiệm, chuyên về siêu âm thai và tư vấn sức khỏe sinh sản.'
            },
            {
                'email': 'doctor.san3@clinic.com',
                'full_name': 'TS. BS. Trần Thị Nga',
                'phone_num': '0901115003',
                'title': 'Tiến sĩ, Bác sĩ',
                'specialization': 'Sản phụ khoa',
                'department_name': 'Sản phụ khoa',
                'license_number': 'BS016',
                'experience_years': 12,
                'consultation_fee': 350000,
                'rating': 4.8,
                'total_reviews': 58,
                'bio': 'Tiến sĩ, Bác sĩ chuyên khoa Sản phụ khoa với 12 năm kinh nghiệm, chuyên về phẫu thuật sản phụ khoa và điều trị vô sinh.'
            },
        ]
        
        for data in doctors_data:
            user, user_created = User.objects.get_or_create(
                email = data["email"],
                defaults={
                    "full_name": data["full_name"],
                    "role": "doctor",
                    "phone_num": data["phone_num"],
                }
            )
            
            # Lấy department dựa trên department_name
            department = Department.objects.filter(name=data['department_name']).first()
            if not department:
                # Nếu không tìm thấy, lấy department đầu tiên hoặc tạo mới
                department = Department.objects.first()
                if not department:
                    self.stdout.write(self.style.WARNING(f'No department found for {data["full_name"]}. Please run seed_departments first.'))
                    continue
            
            # Kiểm tra xem doctor đã tồn tại chưa (theo license_number)
            doctor, doctor_created = Doctor.objects.get_or_create(
                license_number=data['license_number'],
                defaults={
                    'user': user,
                    'department': department,
                    'title': data['title'],
                    'specialization': data['specialization'],
                    'experience_years': data['experience_years'],
                    'consultation_fee': data['consultation_fee'],
                    'rating': data.get('rating', 0.00),
                    'total_reviews': data.get('total_reviews', 0),
                    'bio': data.get('bio', '')
                }
            )
            
            if user_created:
                user.set_password("doctor123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {data["full_name"]}'))
            
            if doctor_created:
                self.stdout.write(self.style.SUCCESS(f'Created doctor: {data["full_name"]} - {department.name}'))
            else:
                # Nếu doctor đã tồn tại, cập nhật thông tin nếu cần
                self.stdout.write(f'Doctor already exists: {data["full_name"]} (License: {data["license_number"]})')
                
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