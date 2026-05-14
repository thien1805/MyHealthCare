from django.core.management.base import BaseCommand
from apps.appointments.models import Department, Service, Room


class Command(BaseCommand):
    help = "Seed database with departments, services, and rooms"
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding departments, services, and rooms...")
        
        # Departments data
        departments_data = [
            {
                'name': 'Nhi khoa',
                'icon': '👶',
                'description': 'Khoa Nhi - Chăm sóc sức khỏe trẻ em',
                'health_examination_fee': 200000.00,
                'services': [
                    {'name': 'Khám tổng quát trẻ em', 'price': 300000.00, 'description': 'Khám sức khỏe tổng quát cho trẻ em'},
                    {'name': 'Tiêm chủng', 'price': 150000.00, 'description': 'Dịch vụ tiêm chủng cho trẻ em'},
                    {'name': 'Tư vấn dinh dưỡng', 'price': 200000.00, 'description': 'Tư vấn dinh dưỡng cho trẻ em'},
                ],
                'rooms': [
                    {'room_number': '101', 'floor': 1},
                    {'room_number': '102', 'floor': 1},
                ]
            },
            {
                'name': 'Tim mạch',
                'icon': '❤️',
                'description': 'Khoa Tim mạch - Chăm sóc sức khỏe tim mạch',
                'health_examination_fee': 300000.00,
                'services': [
                    {'name': 'Điện tâm đồ (ECG)', 'price': 500000.00, 'description': 'Đo điện tâm đồ'},
                    {'name': 'Siêu âm tim', 'price': 800000.00, 'description': 'Siêu âm tim'},
                    {'name': 'Xét nghiệm máu tim mạch', 'price': 600000.00, 'description': 'Xét nghiệm các chỉ số tim mạch'},
                ],
                'rooms': [
                    {'room_number': '201', 'floor': 2},
                    {'room_number': '202', 'floor': 2},
                ]
            },
            {
                'name': 'Nội tiết',
                'icon': '⚕️',
                'description': 'Khoa Nội tiết - Chăm sóc các bệnh nội tiết',
                'health_examination_fee': 250000.00,
                'services': [
                    {'name': 'Xét nghiệm đường huyết', 'price': 200000.00, 'description': 'Xét nghiệm đường huyết'},
                    {'name': 'Xét nghiệm hormone', 'price': 500000.00, 'description': 'Xét nghiệm hormone'},
                    {'name': 'Tư vấn dinh dưỡng đái tháo đường', 'price': 300000.00, 'description': 'Tư vấn dinh dưỡng cho bệnh nhân đái tháo đường'},
                ],
                'rooms': [
                    {'room_number': '301', 'floor': 3},
                ]
            },
            {
                'name': 'Da liễu',
                'icon': '✨',
                'description': 'Khoa Da liễu - Chăm sóc da và điều trị các bệnh về da',
                'health_examination_fee': 200000.00,
                'services': [
                    {'name': 'Khám da liễu tổng quát', 'price': 300000.00, 'description': 'Khám và tư vấn các vấn đề về da'},
                    {'name': 'Điều trị mụn', 'price': 500000.00, 'description': 'Điều trị mụn trứng cá'},
                    {'name': 'Điều trị nám, tàn nhang', 'price': 1000000.00, 'description': 'Điều trị nám và tàn nhang'},
                ],
                'rooms': [
                    {'room_number': '401', 'floor': 4},
                    {'room_number': '402', 'floor': 4},
                ]
            },
            {
                'name': 'Sản phụ khoa',
                'icon': '🤰',
                'description': 'Khoa Sản phụ khoa - Chăm sóc sức khỏe phụ nữ',
                'health_examination_fee': 250000.00,
                'services': [
                    {'name': 'Siêu âm thai', 'price': 400000.00, 'description': 'Siêu âm thai nhi'},
                    {'name': 'Khám phụ khoa', 'price': 350000.00, 'description': 'Khám phụ khoa định kỳ'},
                    {'name': 'Xét nghiệm PAP smear', 'price': 500000.00, 'description': 'Xét nghiệm tầm soát ung thư cổ tử cung'},
                ],
                'rooms': [
                    {'room_number': '501', 'floor': 5},
                ]
            },
        ]
        
        # Create departments, services, and rooms
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={
                    'icon': dept_data['icon'],
                    'description': dept_data['description'],
                    'health_examination_fee': dept_data['health_examination_fee'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created department: {department.name}'))
            else:
                self.stdout.write(f'Department already exists: {department.name}')
            
            # Create services for this department
            for service_data in dept_data['services']:
                service, created = Service.objects.get_or_create(
                    department=department,
                    name=service_data['name'],
                    defaults={
                        'price': service_data['price'],
                        'description': service_data['description'],
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created service: {service.name}'))
            
            # Create rooms for this department
            for room_data in dept_data['rooms']:
                room, created = Room.objects.get_or_create(
                    department=department,
                    room_number=room_data['room_number'],
                    defaults={
                        'floor': room_data['floor'],
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created room: {room.room_number}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Seeding completed!'))

