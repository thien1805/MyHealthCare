from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User, Patient, Doctor
from apps.appointments.models import Department, Room
from datetime import date
import random


class Command(BaseCommand):
    help = "Seed database with full sample data - doctors and patients for all departments"

    def handle(self, *args, **kwargs):
        self.stdout.write("=" * 60)
        self.stdout.write("🏥 Seeding full data for MyHealthCare...")
        self.stdout.write("=" * 60)

        # First, ensure departments exist
        self.create_departments()

        # Then create doctors for each department
        self.create_doctors()

        # Create patients
        self.create_patients()

        # Create admin if not exists
        self.create_admin()

        # Create demo account for portfolio/recruiter testing
        self.create_demo_user()

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully!"))
        self.stdout.write("=" * 60)
        self.print_summary()

    def create_departments(self):
        """Create departments if they don't exist"""
        departments_data = [
            {
                'name': 'Nhi khoa',
                'icon': '👶',
                'description': 'Khoa Nhi - Chăm sóc sức khỏe trẻ em từ sơ sinh đến 18 tuổi',
                'health_examination_fee': 200000.00,
            },
            {
                'name': 'Tim mạch',
                'icon': '❤️',
                'description': 'Khoa Tim mạch - Chẩn đoán và điều trị các bệnh tim mạch',
                'health_examination_fee': 300000.00,
            },
            {
                'name': 'Nội tiết',
                'icon': '⚕️',
                'description': 'Khoa Nội tiết - Điều trị các rối loạn nội tiết, đái tháo đường',
                'health_examination_fee': 250000.00,
            },
            {
                'name': 'Da liễu',
                'icon': '✨',
                'description': 'Khoa Da liễu - Chăm sóc da và điều trị các bệnh về da',
                'health_examination_fee': 200000.00,
            },
            {
                'name': 'Sản phụ khoa',
                'icon': '🤰',
                'description': 'Khoa Sản phụ khoa - Chăm sóc sức khỏe phụ nữ và thai sản',
                'health_examination_fee': 250000.00,
            },
            {
                'name': 'Thần kinh',
                'icon': '🧠',
                'description': 'Khoa Thần kinh - Điều trị các bệnh liên quan đến hệ thần kinh',
                'health_examination_fee': 350000.00,
            },
            {
                'name': 'Tiêu hóa',
                'icon': '🩺',
                'description': 'Khoa Tiêu hóa - Chẩn đoán và điều trị các bệnh đường tiêu hóa',
                'health_examination_fee': 280000.00,
            },
            {
                'name': 'Xương khớp',
                'icon': '🦴',
                'description': 'Khoa Xương khớp - Điều trị các bệnh về cơ xương khớp',
                'health_examination_fee': 280000.00,
            },
            {
                'name': 'Tai Mũi Họng',
                'icon': '👂',
                'description': 'Khoa Tai Mũi Họng - Điều trị các bệnh về tai, mũi, họng',
                'health_examination_fee': 220000.00,
            },
            {
                'name': 'Mắt',
                'icon': '👁️',
                'description': 'Khoa Mắt - Khám và điều trị các bệnh về mắt',
                'health_examination_fee': 250000.00,
            },
        ]

        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={
                    'icon': dept_data['icon'],
                    'description': dept_data['description'],
                    'health_examination_fee': dept_data['health_examination_fee'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f"  ✓ Created department: {dept_data['name']}")
            else:
                self.stdout.write(f"  • Department exists: {dept_data['name']}")

    def create_doctors(self):
        """Create doctors distributed across all departments"""
        self.stdout.write("\n📋 Creating doctors...")

        # Vietnamese names for doctors
        first_names_male = ['Minh', 'Tuấn', 'Hùng', 'Đức', 'Quang', 'Thành', 'Long', 'Hoàng', 'Khoa', 'Phú']
        first_names_female = ['Hương', 'Lan', 'Mai', 'Hoa', 'Linh', 'Ngọc', 'Thảo', 'Yến', 'Trang', 'Hạnh']
        last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Đỗ', 'Bùi', 'Đặng', 'Võ']
        middle_names = ['Văn', 'Thị', 'Minh', 'Anh', 'Quốc', 'Hữu', 'Thanh', 'Bảo', 'Gia', 'Như']

        titles = ['BS.', 'ThS. BS.', 'TS. BS.', 'PGS. TS. BS.']
        title_weights = [0.4, 0.35, 0.2, 0.05]  # More junior doctors

        # Avatar URLs (placeholder)
        avatar_base = "https://ui-avatars.com/api/?name={}&background=random&size=200"

        departments = Department.objects.filter(is_active=True)
        
        doctor_count = 0
        license_counter = 100

        for dept in departments:
            # 3-5 doctors per department
            num_doctors = random.randint(3, 5)
            
            for i in range(num_doctors):
                license_counter += 1
                is_female = random.random() > 0.5
                
                first_name = random.choice(first_names_female if is_female else first_names_male)
                last_name = random.choice(last_names)
                middle_name = random.choice(middle_names)
                full_name = f"{last_name} {middle_name} {first_name}"
                
                title = random.choices(titles, weights=title_weights)[0]
                
                # Experience based on title
                if 'PGS' in title:
                    experience = random.randint(20, 30)
                    fee = random.randint(500000, 800000)
                elif 'TS' in title:
                    experience = random.randint(12, 20)
                    fee = random.randint(350000, 500000)
                elif 'ThS' in title:
                    experience = random.randint(8, 15)
                    fee = random.randint(280000, 400000)
                else:
                    experience = random.randint(3, 10)
                    fee = random.randint(200000, 300000)

                # Rating and reviews
                rating = round(random.uniform(4.0, 5.0), 2)
                total_reviews = random.randint(10, 150)

                email = f"doctor.{dept.name.lower().replace(' ', '')}_{i+1}@myhealthcare.com"
                phone = f"090{random.randint(1000000, 9999999)}"
                license_number = f"BS{license_counter:05d}"

                bio = self.generate_doctor_bio(title, full_name, dept.name, experience)
                avatar_url = avatar_base.format(full_name.replace(' ', '+'))

                # Create user
                user, user_created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "full_name": f"{title} {full_name}",
                        "role": "doctor",
                        "phone_num": phone,
                    }
                )
                if user_created:
                    user.set_password("doctor123")
                    user.save()

                # Create or get room for doctor
                room, _ = Room.objects.get_or_create(
                    room_number=f"P{dept.id}{i+1:02d}",
                    defaults={
                        'floor': dept.id,
                        'department': dept,
                        'is_active': True
                    }
                )

                # Create doctor profile
                doctor, doctor_created = Doctor.objects.get_or_create(
                    license_number=license_number,
                    defaults={
                        'user': user,
                        'department': dept,
                        'room': room,
                        'title': title,
                        'specialization': dept.name,
                        'experience_years': experience,
                        'consultation_fee': fee,
                        'rating': rating,
                        'total_reviews': total_reviews,
                        'bio': bio,
                        'avatar_url': avatar_url,
                    }
                )

                if doctor_created:
                    doctor_count += 1
                    self.stdout.write(f"  ✓ {title} {full_name} - {dept.name}")

        self.stdout.write(self.style.SUCCESS(f"\n  📊 Total doctors created: {doctor_count}"))

    def generate_doctor_bio(self, title, name, department, experience):
        """Generate a realistic bio for doctor"""
        bios = [
            f"{title} {name} là bác sĩ chuyên khoa {department} với {experience} năm kinh nghiệm. Tốt nghiệp Đại học Y khoa Hà Nội, từng công tác tại nhiều bệnh viện lớn.",
            f"Với {experience} năm trong ngành y, {title} {name} là chuyên gia hàng đầu về {department}. Được đào tạo chuyên sâu tại Đức và Nhật Bản.",
            f"{title} {name} có {experience} năm kinh nghiệm trong lĩnh vực {department}. Tận tâm với bệnh nhân, luôn cập nhật kiến thức y khoa mới nhất.",
            f"Bác sĩ {name} chuyên khoa {department}, {experience} năm kinh nghiệm. Đã điều trị thành công cho hàng nghìn bệnh nhân với các phương pháp tiên tiến.",
        ]
        return random.choice(bios)

    def create_patients(self):
        """Create sample patients"""
        self.stdout.write("\n👥 Creating patients...")

        # Vietnamese names
        first_names_male = ['An', 'Bình', 'Cường', 'Dũng', 'Hải', 'Khang', 'Long', 'Nam', 'Phong', 'Quân', 
                           'Sơn', 'Thắng', 'Trung', 'Việt', 'Xuân']
        first_names_female = ['An', 'Bích', 'Chi', 'Diễm', 'Hà', 'Hương', 'Lan', 'Mai', 'Ngọc', 'Oanh',
                             'Phương', 'Quỳnh', 'Thanh', 'Uyên', 'Yến']
        last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Đỗ', 'Bùi', 'Đặng', 'Võ',
                      'Phan', 'Lý', 'Hồ', 'Đinh', 'Tạ']
        middle_names = ['Văn', 'Thị', 'Minh', 'Anh', 'Quốc', 'Hữu', 'Thanh', 'Bảo', 'Gia', 'Như',
                        'Xuân', 'Thu', 'Hồng', 'Kim', 'Ngọc']

        # HCMC districts
        districts = ['Quận 1', 'Quận 3', 'Quận 5', 'Quận 7', 'Quận 10', 'Quận Bình Thạnh', 
                     'Quận Tân Bình', 'Quận Phú Nhuận', 'Thủ Đức', 'Quận Gò Vấp']
        streets = ['Nguyễn Huệ', 'Lê Lợi', 'Trần Hưng Đạo', 'Điện Biên Phủ', 'Cách Mạng Tháng 8',
                   'Nam Kỳ Khởi Nghĩa', 'Hai Bà Trưng', 'Võ Văn Tần', 'Nguyễn Thị Minh Khai', 'Hoàng Văn Thụ']

        patient_count = 0
        
        # Create 30 patients
        for i in range(1, 31):
            is_female = random.random() > 0.5
            gender = 'female' if is_female else 'male'
            
            first_name = random.choice(first_names_female if is_female else first_names_male)
            last_name = random.choice(last_names)
            middle_name = random.choice(middle_names)
            full_name = f"{last_name} {middle_name} {first_name}"

            # Random birth date between 1950 and 2010
            year = random.randint(1950, 2010)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            dob = date(year, month, day)

            email = f"patient{i}@gmail.com"
            phone = f"09{random.randint(10000000, 99999999)}"
            
            # Address
            street_num = random.randint(1, 500)
            address = f"{street_num} {random.choice(streets)}, {random.choice(districts)}, TP.HCM"
            
            # Insurance ID
            insurance_id = f"HS{random.randint(1000000000, 9999999999)}"
            
            # Emergency contact
            emergency_name = f"{random.choice(last_names)} {random.choice(middle_names)} {random.choice(first_names_male if random.random() > 0.5 else first_names_female)}"
            emergency_phone = f"09{random.randint(10000000, 99999999)}"

            # Create user
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": full_name,
                    "role": "patient",
                    "phone_num": phone,
                }
            )
            
            if user_created:
                user.set_password("patient123")
                user.save()

                # Create patient profile
                Patient.objects.create(
                    user=user,
                    date_of_birth=dob,
                    gender=gender,
                    address=address,
                    insurance_id=insurance_id,
                    emergency_contact=emergency_name,
                    emergency_contact_phone=emergency_phone[:10]  # Ensure 10 digits
                )
                
                patient_count += 1
                self.stdout.write(f"  ✓ {full_name} ({email})")

        self.stdout.write(self.style.SUCCESS(f"\n  📊 Total patients created: {patient_count}"))

    def create_admin(self):
        """Create admin user if not exists"""
        self.stdout.write("\n👤 Creating admin...")
        
        admin, created = User.objects.get_or_create(
            email="admin@myhealthcare.com",
            defaults={
                "full_name": "Administrator",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Admin user created"))
        else:
            self.stdout.write("  • Admin user already exists")

    def create_demo_user(self):
        """Create a demo patient account for easy portfolio testing"""
        self.stdout.write("\n👥 Creating demo patient account...")
        demo_email = "demo@myhealthcare.com"
        demo_password = "demo123"

        demo_user, created = User.objects.get_or_create(
            email=demo_email,
            defaults={
                "full_name": "Demo Patient",
                "role": "patient",
                "is_active": True,
            }
        )

        if created:
            demo_user.set_password(demo_password)
            demo_user.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Demo user created"))
        else:
            self.stdout.write("  • Demo user already exists")

        Patient.objects.get_or_create(
            user=demo_user,
            defaults={
                'date_of_birth': '1990-01-01',
                'gender': 'other',
                'address': 'Demo patient account for portfolio testing',
                'insurance_id': 'DEMO001'
            }
        )
        self.stdout.write(f"  • Credential: {demo_email} / {demo_password}")

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write("\n📋 SUMMARY")
        self.stdout.write("-" * 40)
        
        # Count by department
        self.stdout.write("\n🏥 Departments:")
        for dept in Department.objects.filter(is_active=True):
            doctor_count = Doctor.objects.filter(department=dept).count()
            self.stdout.write(f"  • {dept.name}: {doctor_count} doctors")
        
        total_doctors = Doctor.objects.count()
        total_patients = Patient.objects.count()
        total_users = User.objects.count()
        
        self.stdout.write(f"\n📊 Total Statistics:")
        self.stdout.write(f"  • Total Users: {total_users}")
        self.stdout.write(f"  • Total Doctors: {total_doctors}")
        self.stdout.write(f"  • Total Patients: {total_patients}")
        
        self.stdout.write("\n🔐 Login Credentials:")
        self.stdout.write("  Admin:   admin@myhealthcare.com / admin123")
        self.stdout.write("  Demo:    demo@myhealthcare.com / demo123")
        self.stdout.write("  Doctor:  doctor.{dept}_1@myhealthcare.com / doctor123")
        self.stdout.write("  Patient: patient1@gmail.com / patient123")
