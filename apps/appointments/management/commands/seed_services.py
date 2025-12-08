from django.core.management.base import BaseCommand
from apps.appointments.models import Department, Service


class Command(BaseCommand):
    help = "Seed database with comprehensive services for each department"
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding comprehensive services for all departments...")
        
        # Services data for each department
        services_by_department = {
            'Nhi khoa': [
                {'name': 'Khám tổng quát trẻ em', 'price': 300000.00, 'description': 'Khám sức khỏe tổng quát cho trẻ em'},
                {'name': 'Tiêm chủng', 'price': 150000.00, 'description': 'Dịch vụ tiêm chủng cho trẻ em'},
                {'name': 'Tư vấn dinh dưỡng trẻ em', 'price': 200000.00, 'description': 'Tư vấn dinh dưỡng cho trẻ em'},
                {'name': 'Khám sơ sinh', 'price': 350000.00, 'description': 'Khám sức khỏe cho trẻ sơ sinh'},
                {'name': 'Điều trị nhiễm trùng đường hô hấp', 'price': 400000.00, 'description': 'Điều trị các bệnh nhiễm trùng đường hô hấp ở trẻ'},
                {'name': 'Tư vấn phát triển trẻ em', 'price': 250000.00, 'description': 'Đánh giá và tư vấn sự phát triển của trẻ'},
                {'name': 'Xét nghiệm máu trẻ em', 'price': 180000.00, 'description': 'Xét nghiệm máu định kỳ cho trẻ'},
                {'name': 'Siêu âm nhi khoa', 'price': 350000.00, 'description': 'Siêu âm chẩn đoán cho trẻ em'},
            ],
            'Tim mạch': [
                {'name': 'Điện tâm đồ (ECG)', 'price': 500000.00, 'description': 'Đo điện tâm đồ'},
                {'name': 'Siêu âm tim', 'price': 800000.00, 'description': 'Siêu âm tim'},
                {'name': 'Xét nghiệm máu tim mạch', 'price': 600000.00, 'description': 'Xét nghiệm các chỉ số tim mạch'},
                {'name': 'Holter ECG 24h', 'price': 1200000.00, 'description': 'Theo dõi nhịp tim 24 giờ'},
                {'name': 'Siêu âm Doppler mạch máu', 'price': 900000.00, 'description': 'Siêu âm Doppler đánh giá mạch máu'},
                {'name': 'Đo huyết áp liên tục 24h', 'price': 500000.00, 'description': 'Theo dõi huyết áp 24 giờ'},
                {'name': 'Tư vấn tim mạch', 'price': 400000.00, 'description': 'Tư vấn bệnh tim mạch và phòng ngừa'},
                {'name': 'Test gắng sức', 'price': 1500000.00, 'description': 'Kiểm tra chức năng tim khi gắng sức'},
            ],
            'Nội tiết': [
                {'name': 'Xét nghiệm đường huyết', 'price': 200000.00, 'description': 'Xét nghiệm đường huyết'},
                {'name': 'Xét nghiệm hormone', 'price': 500000.00, 'description': 'Xét nghiệm hormone'},
                {'name': 'Tư vấn dinh dưỡng đái tháo đường', 'price': 300000.00, 'description': 'Tư vấn dinh dưỡng cho bệnh nhân đái tháo đường'},
                {'name': 'Xét nghiệm HbA1c', 'price': 350000.00, 'description': 'Xét nghiệm chỉ số đường huyết dài hạn'},
                {'name': 'Xét nghiệm tuyến giáp', 'price': 450000.00, 'description': 'Xét nghiệm chức năng tuyến giáp'},
                {'name': 'Siêu âm tuyến giáp', 'price': 400000.00, 'description': 'Siêu âm đánh giá tuyến giáp'},
                {'name': 'Tư vấn quản lý cân nặng', 'price': 350000.00, 'description': 'Tư vấn giảm cân và quản lý cân nặng'},
                {'name': 'Xét nghiệm Cortisol', 'price': 400000.00, 'description': 'Xét nghiệm hormone Cortisol'},
            ],
            'Da liễu': [
                {'name': 'Khám da liễu tổng quát', 'price': 300000.00, 'description': 'Khám và tư vấn các vấn đề về da'},
                {'name': 'Điều trị mụn', 'price': 500000.00, 'description': 'Điều trị mụn trứng cá'},
                {'name': 'Điều trị nám, tàn nhang', 'price': 1000000.00, 'description': 'Điều trị nám và tàn nhang'},
                {'name': 'Điều trị viêm da', 'price': 400000.00, 'description': 'Điều trị các loại viêm da'},
                {'name': 'Peel da hóa học', 'price': 800000.00, 'description': 'Làm sạch da bằng phương pháp peel hóa học'},
                {'name': 'Laser trị sẹo', 'price': 1500000.00, 'description': 'Điều trị sẹo bằng laser'},
                {'name': 'Sinh thiết da', 'price': 600000.00, 'description': 'Sinh thiết để chẩn đoán bệnh da'},
                {'name': 'Tư vấn chăm sóc da', 'price': 250000.00, 'description': 'Tư vấn quy trình chăm sóc da'},
            ],
            'Sản phụ khoa': [
                {'name': 'Siêu âm thai', 'price': 400000.00, 'description': 'Siêu âm thai nhi'},
                {'name': 'Khám phụ khoa', 'price': 350000.00, 'description': 'Khám phụ khoa định kỳ'},
                {'name': 'Xét nghiệm PAP smear', 'price': 500000.00, 'description': 'Xét nghiệm tầm soát ung thư cổ tử cung'},
                {'name': 'Siêu âm 4D', 'price': 800000.00, 'description': 'Siêu âm 4D thai nhi'},
                {'name': 'Xét nghiệm tiền sản', 'price': 1200000.00, 'description': 'Bộ xét nghiệm tiền sản toàn diện'},
                {'name': 'Đặt vòng tránh thai', 'price': 500000.00, 'description': 'Dịch vụ đặt vòng tránh thai'},
                {'name': 'Tư vấn kế hoạch hóa gia đình', 'price': 200000.00, 'description': 'Tư vấn các phương pháp tránh thai'},
                {'name': 'Khám vô sinh', 'price': 600000.00, 'description': 'Khám và tư vấn vô sinh'},
            ],
            'Nội khoa': [
                {'name': 'Khám nội khoa tổng quát', 'price': 250000.00, 'description': 'Khám sức khỏe nội khoa tổng quát'},
                {'name': 'Xét nghiệm máu tổng quát', 'price': 400000.00, 'description': 'Bộ xét nghiệm máu cơ bản'},
                {'name': 'Điều trị viêm dạ dày', 'price': 350000.00, 'description': 'Điều trị viêm loét dạ dày'},
                {'name': 'Nội soi dạ dày', 'price': 1500000.00, 'description': 'Nội soi dạ dày - tá tràng'},
                {'name': 'Siêu âm ổ bụng', 'price': 500000.00, 'description': 'Siêu âm ổ bụng tổng quát'},
                {'name': 'Điều trị cao huyết áp', 'price': 300000.00, 'description': 'Tư vấn và điều trị cao huyết áp'},
                {'name': 'Xét nghiệm chức năng gan', 'price': 350000.00, 'description': 'Xét nghiệm đánh giá chức năng gan'},
                {'name': 'Xét nghiệm chức năng thận', 'price': 350000.00, 'description': 'Xét nghiệm đánh giá chức năng thận'},
            ],
            'Internal Medicine': [
                {'name': 'General Internal Medicine Examination', 'price': 250000.00, 'description': 'General internal medicine health check'},
                {'name': 'Complete Blood Count', 'price': 400000.00, 'description': 'Basic blood test panel'},
                {'name': 'Gastritis Treatment', 'price': 350000.00, 'description': 'Treatment for gastritis and stomach ulcers'},
                {'name': 'Gastroscopy', 'price': 1500000.00, 'description': 'Upper GI endoscopy'},
                {'name': 'Abdominal Ultrasound', 'price': 500000.00, 'description': 'General abdominal ultrasound'},
                {'name': 'Hypertension Management', 'price': 300000.00, 'description': 'Consultation and treatment for high blood pressure'},
                {'name': 'Liver Function Test', 'price': 350000.00, 'description': 'Liver function assessment'},
                {'name': 'Kidney Function Test', 'price': 350000.00, 'description': 'Kidney function assessment'},
            ],
            'Cardiology': [
                {'name': 'ECG (Electrocardiogram)', 'price': 500000.00, 'description': 'Electrocardiogram test'},
                {'name': 'Echocardiography', 'price': 800000.00, 'description': 'Heart ultrasound'},
                {'name': 'Cardiovascular Blood Test', 'price': 600000.00, 'description': 'Cardiac markers blood test'},
                {'name': 'Holter 24h Monitoring', 'price': 1200000.00, 'description': '24-hour heart rhythm monitoring'},
                {'name': 'Vascular Doppler Ultrasound', 'price': 900000.00, 'description': 'Doppler ultrasound for blood vessels'},
                {'name': '24h Blood Pressure Monitoring', 'price': 500000.00, 'description': '24-hour blood pressure monitoring'},
                {'name': 'Cardiology Consultation', 'price': 400000.00, 'description': 'Heart disease consultation and prevention'},
                {'name': 'Stress Test', 'price': 1500000.00, 'description': 'Cardiac stress testing'},
            ],
            'Orthopedics': [
                {'name': 'Orthopedic Consultation', 'price': 300000.00, 'description': 'General orthopedic examination'},
                {'name': 'X-Ray Imaging', 'price': 350000.00, 'description': 'X-ray for bone and joint evaluation'},
                {'name': 'MRI Scan', 'price': 2500000.00, 'description': 'Magnetic resonance imaging'},
                {'name': 'Joint Injection', 'price': 800000.00, 'description': 'Intra-articular injection therapy'},
                {'name': 'Physical Therapy Session', 'price': 400000.00, 'description': 'Physical therapy rehabilitation'},
                {'name': 'Bone Density Test', 'price': 600000.00, 'description': 'DEXA scan for bone density'},
                {'name': 'Sports Injury Treatment', 'price': 500000.00, 'description': 'Treatment for sports-related injuries'},
                {'name': 'Cast Application', 'price': 450000.00, 'description': 'Fracture casting service'},
            ],
            'Ophthalmology': [
                {'name': 'Eye Examination', 'price': 250000.00, 'description': 'Comprehensive eye examination'},
                {'name': 'Vision Test', 'price': 150000.00, 'description': 'Visual acuity testing'},
                {'name': 'Fundus Examination', 'price': 400000.00, 'description': 'Retinal examination'},
                {'name': 'Glaucoma Screening', 'price': 500000.00, 'description': 'Intraocular pressure and glaucoma test'},
                {'name': 'Cataract Consultation', 'price': 350000.00, 'description': 'Cataract evaluation and consultation'},
                {'name': 'Contact Lens Fitting', 'price': 300000.00, 'description': 'Contact lens fitting and prescription'},
                {'name': 'Laser Eye Surgery Consultation', 'price': 500000.00, 'description': 'LASIK consultation'},
                {'name': 'OCT Scan', 'price': 600000.00, 'description': 'Optical coherence tomography'},
            ],
            'ENT (Ear, Nose, Throat)': [
                {'name': 'ENT Examination', 'price': 250000.00, 'description': 'General ENT checkup'},
                {'name': 'Hearing Test', 'price': 400000.00, 'description': 'Audiometry hearing assessment'},
                {'name': 'Nasal Endoscopy', 'price': 600000.00, 'description': 'Endoscopic nasal examination'},
                {'name': 'Throat Examination', 'price': 200000.00, 'description': 'Throat and larynx examination'},
                {'name': 'Sinusitis Treatment', 'price': 400000.00, 'description': 'Treatment for sinus infections'},
                {'name': 'Tinnitus Consultation', 'price': 350000.00, 'description': 'Consultation for ringing in ears'},
                {'name': 'Sleep Apnea Screening', 'price': 800000.00, 'description': 'Sleep apnea evaluation'},
                {'name': 'Voice Therapy', 'price': 450000.00, 'description': 'Voice and speech therapy'},
            ],
            'Neurology': [
                {'name': 'Neurological Examination', 'price': 400000.00, 'description': 'Comprehensive neurological assessment'},
                {'name': 'EEG (Electroencephalogram)', 'price': 800000.00, 'description': 'Brain wave recording'},
                {'name': 'Brain MRI', 'price': 3000000.00, 'description': 'Magnetic resonance imaging of brain'},
                {'name': 'Headache Treatment', 'price': 350000.00, 'description': 'Migraine and headache consultation'},
                {'name': 'Nerve Conduction Study', 'price': 1000000.00, 'description': 'Nerve function testing'},
                {'name': 'Stroke Prevention Consultation', 'price': 400000.00, 'description': 'Stroke risk assessment'},
                {'name': 'Memory Assessment', 'price': 500000.00, 'description': 'Cognitive and memory testing'},
                {'name': 'Parkinson Consultation', 'price': 450000.00, 'description': 'Parkinson disease evaluation'},
            ],
            'Dentistry': [
                {'name': 'Dental Checkup', 'price': 200000.00, 'description': 'Routine dental examination'},
                {'name': 'Teeth Cleaning', 'price': 350000.00, 'description': 'Professional dental cleaning'},
                {'name': 'Tooth Filling', 'price': 400000.00, 'description': 'Dental filling for cavities'},
                {'name': 'Tooth Extraction', 'price': 500000.00, 'description': 'Tooth extraction service'},
                {'name': 'Root Canal Treatment', 'price': 1500000.00, 'description': 'Root canal therapy'},
                {'name': 'Teeth Whitening', 'price': 1200000.00, 'description': 'Professional teeth whitening'},
                {'name': 'Dental X-Ray', 'price': 250000.00, 'description': 'Dental radiograph'},
                {'name': 'Orthodontic Consultation', 'price': 300000.00, 'description': 'Braces and alignment consultation'},
            ],
            'Psychiatry': [
                {'name': 'Psychiatric Consultation', 'price': 500000.00, 'description': 'Mental health evaluation'},
                {'name': 'Depression Treatment', 'price': 400000.00, 'description': 'Treatment for depression'},
                {'name': 'Anxiety Management', 'price': 400000.00, 'description': 'Treatment for anxiety disorders'},
                {'name': 'Sleep Disorder Consultation', 'price': 450000.00, 'description': 'Insomnia and sleep issues'},
                {'name': 'Psychological Testing', 'price': 800000.00, 'description': 'Psychological assessment'},
                {'name': 'Stress Management Counseling', 'price': 350000.00, 'description': 'Stress management therapy'},
                {'name': 'ADHD Evaluation', 'price': 600000.00, 'description': 'Attention deficit evaluation'},
                {'name': 'Therapy Session', 'price': 500000.00, 'description': 'Individual psychotherapy session'},
            ],
        }
        
        created_count = 0
        skipped_count = 0
        
        for dept_name, services in services_by_department.items():
            # Try to find the department
            department = Department.objects.filter(name=dept_name).first()
            
            if not department:
                self.stdout.write(self.style.WARNING(f'Department not found: {dept_name} - Creating it...'))
                department = Department.objects.create(
                    name=dept_name,
                    icon='🏥',
                    description=f'{dept_name} Department',
                    health_examination_fee=200000.00,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'  Created department: {dept_name}'))
            
            self.stdout.write(f'\n📁 {dept_name}:')
            
            for service_data in services:
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
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Created: {service.name} - {service.price:,.0f}₫'))
                else:
                    skipped_count += 1
                    self.stdout.write(f'  ⏭️  Exists: {service.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Seeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created_count} services'))
        self.stdout.write(f'   Skipped: {skipped_count} services (already existed)')
