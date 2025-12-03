from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
# Thay 'your_app' bằng tên app chứa model Doctor của bạn
from apps.accounts.models import Doctor 
# Thay 'appointments' bằng tên app chứa model Department (dựa trên ForeignKey bạn khai báo)
from apps.appointments.models import Department 

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo tự động 20 user role doctor và profile doctor'

    def handle(self, *args, **kwargs):
        self.stdout.write('Bắt đầu tạo dữ liệu Doctor...')

        # Vì Doctor bắt buộc phải thuộc 1 Department, ta cần lấy hoặc tạo 1 cái mẫu
        # Nếu chưa có department nào, code này sẽ tạo 1 cái tên là "General Medicine"
        dept, _ = Department.objects.get_or_create(
            name="Tim mạch",
            defaults={'description': "Tim mạch"}
        )

        created_count = 0
        
        # Dùng transaction để đảm bảo nếu lỗi thì không tạo dữ liệu rác
        with transaction.atomic():
            for i in range(1, 21):
                email = f"doctor{i}@myhealthcare.com"
                password = f"doctor{i}"
                full_name = f"Doctor Number {i}"
                license_no = f"LIC-2024-{i:03d}" # Tạo mã giấy phép unique để không lỗi DB

                # Kiểm tra xem user đã tồn tại chưa để tránh lỗi Duplicate
                if not User.objects.filter(email=email).exists():
                    # 1. Tạo User
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        full_name=full_name,
                        role='doctor',
                        is_staff=False # Doctor thường không cần vào trang admin django
                    )

                    # 2. Tạo Doctor Profile (Bắt buộc vì quan hệ OneToOne)
                    Doctor.objects.create(
                        user=user,
                        department=dept,
                        license_number=license_no,
                        title="Dr.",
                        specialization="General Medicine",
                        experience_years=5,
                        bio=f"This is an auto-generated bio for {full_name}",
                        consultation_fee=500000.00
                    )
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Đã tạo: {email}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Bỏ qua: {email} (Đã tồn tại)'))

        self.stdout.write(self.style.SUCCESS(f'--- HOÀN TẤT: Đã tạo mới {created_count} bác sĩ ---'))
        