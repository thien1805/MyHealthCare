from django.core.management.base import BaseCommand
from apps.appointments.models import Department, Service, Room


class Command(BaseCommand):
    help = "Seed database with English departments, services, and rooms"
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding English departments, services, and rooms...")
        
        # Departments data (English)
        departments_data = [
            {
                'name': 'Pediatrics',
                'icon': '👶',
                'description': 'Medical care for infants, children, and adolescents',
                'health_examination_fee': 200000.00,
                'services': [
                    {'name': 'General Child Examination', 'price': 300000.00, 'description': 'Comprehensive health check-up for children'},
                    {'name': 'Vaccination Services', 'price': 150000.00, 'description': 'Immunization and vaccination for children'},
                    {'name': 'Nutritional Counseling', 'price': 200000.00, 'description': 'Dietary guidance for child development'},
                ],
                'rooms': [
                    {'room_number': '101', 'floor': 1},
                    {'room_number': '102', 'floor': 1},
                ]
            },
            {
                'name': 'Cardiology',
                'icon': '❤️',
                'description': 'Heart and cardiovascular diseases treatment and management',
                'health_examination_fee': 300000.00,
                'services': [
                    {'name': 'Electrocardiogram (ECG)', 'price': 500000.00, 'description': 'Heart rhythm and electrical activity assessment'},
                    {'name': 'Echocardiography', 'price': 800000.00, 'description': 'Ultrasound imaging of the heart'},
                    {'name': 'Cardiac Blood Tests', 'price': 600000.00, 'description': 'Laboratory tests for cardiac markers and risk factors'},
                ],
                'rooms': [
                    {'room_number': '201', 'floor': 2},
                    {'room_number': '202', 'floor': 2},
                ]
            },
            {
                'name': 'Endocrinology',
                'icon': '⚕️',
                'description': 'Diagnosis and treatment of hormonal and metabolic disorders',
                'health_examination_fee': 250000.00,
                'services': [
                    {'name': 'Blood Sugar Testing', 'price': 200000.00, 'description': 'Glucose level measurement and diabetes screening'},
                    {'name': 'Hormone Panel Test', 'price': 500000.00, 'description': 'Comprehensive hormonal assessment'},
                    {'name': 'Diabetes Nutritional Counseling', 'price': 300000.00, 'description': 'Dietary management for diabetic patients'},
                ],
                'rooms': [
                    {'room_number': '301', 'floor': 3},
                ]
            },
            {
                'name': 'Dermatology',
                'icon': '✨',
                'description': 'Treatment of skin conditions, diseases, and cosmetic concerns',
                'health_examination_fee': 200000.00,
                'services': [
                    {'name': 'General Dermatology Consultation', 'price': 300000.00, 'description': 'Evaluation and counseling for skin problems'},
                    {'name': 'Acne Treatment', 'price': 500000.00, 'description': 'Treatment for acne and related skin conditions'},
                    {'name': 'Hyperpigmentation Treatment', 'price': 1000000.00, 'description': 'Treatment for age spots and skin pigmentation issues'},
                ],
                'rooms': [
                    {'room_number': '401', 'floor': 4},
                    {'room_number': '402', 'floor': 4},
                ]
            },
            {
                'name': 'Obstetrics & Gynecology',
                'icon': '🤰',
                'description': 'Comprehensive care for pregnancy, childbirth, and reproductive health',
                'health_examination_fee': 250000.00,
                'services': [
                    {'name': 'Obstetric Ultrasound', 'price': 400000.00, 'description': 'Pregnancy monitoring and fetal assessment'},
                    {'name': 'Gynecological Examination', 'price': 350000.00, 'description': 'Regular women\'s health check-up'},
                    {'name': 'Cervical Cancer Screening (Pap Test)', 'price': 500000.00, 'description': 'Early detection of cervical abnormalities'},
                ],
                'rooms': [
                    {'room_number': '501', 'floor': 5},
                ]
            },
            {
                'name': 'Respiratory Medicine',
                'icon': '🫁',
                'description': 'Treatment of lung and respiratory tract diseases',
                'health_examination_fee': 220000.00,
                'services': [
                    {'name': 'Chest X-Ray', 'price': 250000.00, 'description': 'Radiographic imaging of chest and lungs'},
                    {'name': 'Pulmonary Function Test', 'price': 400000.00, 'description': 'Assessment of lung capacity and function'},
                    {'name': 'Bronchitis and Asthma Treatment Consultation', 'price': 300000.00, 'description': 'Management plan for respiratory conditions'},
                ],
                'rooms': [
                    {'room_number': '601', 'floor': 6},
                ]
            },
            {
                'name': 'Orthopedics',
                'icon': '🦴',
                'description': 'Treatment of bones, joints, ligaments, and muscle disorders',
                'health_examination_fee': 240000.00,
                'services': [
                    {'name': 'Bone and Joint Examination', 'price': 350000.00, 'description': 'Comprehensive musculoskeletal assessment'},
                    {'name': 'X-Ray and Imaging', 'price': 300000.00, 'description': 'Radiographic evaluation of bones and joints'},
                    {'name': 'Physical Therapy Consultation', 'price': 250000.00, 'description': 'Rehabilitation and recovery planning'},
                ],
                'rooms': [
                    {'room_number': '701', 'floor': 7},
                    {'room_number': '702', 'floor': 7},
                ]
            },
            {
                'name': 'Neurology',
                'icon': '🧠',
                'description': 'Diagnosis and treatment of nervous system disorders',
                'health_examination_fee': 280000.00,
                'services': [
                    {'name': 'Neurological Examination', 'price': 400000.00, 'description': 'Assessment of nervous system function'},
                    {'name': 'EEG (Electroencephalogram)', 'price': 600000.00, 'description': 'Brain electrical activity recording'},
                    {'name': 'Headache and Migraine Management', 'price': 350000.00, 'description': 'Diagnosis and treatment plan for headaches'},
                ],
                'rooms': [
                    {'room_number': '801', 'floor': 8},
                ]
            },
            {
                'name': 'Internal Medicine',
                'icon': '👨‍⚕️',
                'description': 'General diagnosis and treatment of internal organ diseases',
                'health_examination_fee': 200000.00,
                'services': [
                    {'name': 'General Health Check-up', 'price': 400000.00, 'description': 'Comprehensive physical examination'},
                    {'name': 'Laboratory Tests Panel', 'price': 500000.00, 'description': 'Complete blood work and metabolic testing'},
                    {'name': 'Chronic Disease Management', 'price': 300000.00, 'description': 'Management of long-term health conditions'},
                ],
                'rooms': [
                    {'room_number': '901', 'floor': 9},
                    {'room_number': '902', 'floor': 9},
                ]
            },
            {
                'name': 'Ophthalmology',
                'icon': '👁️',
                'description': 'Comprehensive eye care and treatment of eye diseases',
                'health_examination_fee': 180000.00,
                'services': [
                    {'name': 'Eye Examination and Vision Testing', 'price': 250000.00, 'description': 'Comprehensive vision assessment'},
                    {'name': 'Glasses and Contact Lens Fitting', 'price': 300000.00, 'description': 'Prescription and fitting services'},
                    {'name': 'Cataract and Glaucoma Evaluation', 'price': 600000.00, 'description': 'Screening for eye diseases'},
                ],
                'rooms': [
                    {'room_number': '1001', 'floor': 10},
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
                self.stdout.write(self.style.SUCCESS(f'✅ Created department: {department.name}'))
            else:
                self.stdout.write(f'⚠️  Department already exists: {department.name}')
            
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
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created service: {service.name}'))
            
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
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created room: {room.room_number} (Floor {room.floor})'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ English departments seeding completed successfully!'))
        self.stdout.write(self.style.WARNING(f'\n📊 Summary:'))
        self.stdout.write(f'  • Total Departments: {Department.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  • Total Services: {Service.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  • Total Rooms: {Room.objects.filter(is_active=True).count()}')
