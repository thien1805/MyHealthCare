from django.core.management.base import BaseCommand
from apps.appointments.models import Department, Service


class Command(BaseCommand):
    help = "Update existing departments and services with English localization data"
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Updating departments and services with English localization...")
        
        # Department translations (Vietnamese name -> English name)
        department_translations = {
            'Nhi khoa': {'name_en': 'Pediatrics', 'description_en': 'Pediatric Department - Children\'s healthcare'},
            'Tim mạch': {'name_en': 'Cardiology', 'description_en': 'Cardiology Department - Heart and cardiovascular care'},
            'Nội tiết': {'name_en': 'Endocrinology', 'description_en': 'Endocrinology Department - Hormonal and metabolic disorders'},
            'Da liễu': {'name_en': 'Dermatology', 'description_en': 'Dermatology Department - Skin care and treatment'},
            'Sản phụ khoa': {'name_en': 'Obstetrics & Gynecology', 'description_en': 'OB/GYN Department - Women\'s health care'},
            'Nội khoa': {'name_en': 'Internal Medicine', 'description_en': 'Internal Medicine Department - General healthcare'},
            'Internal Medicine': {'name_en': 'Internal Medicine', 'description_en': 'Internal Medicine Department - General healthcare'},
            'Cardiology': {'name_en': 'Cardiology', 'description_en': 'Cardiology Department - Heart care'},
            'Orthopedics': {'name_en': 'Orthopedics', 'description_en': 'Orthopedics Department - Bone and joint care'},
            'Ophthalmology': {'name_en': 'Ophthalmology', 'description_en': 'Ophthalmology Department - Eye care'},
            'ENT (Ear, Nose, Throat)': {'name_en': 'ENT (Ear, Nose, Throat)', 'description_en': 'ENT Department - Ear, nose and throat care'},
            'Neurology': {'name_en': 'Neurology', 'description_en': 'Neurology Department - Brain and nervous system care'},
            'Dentistry': {'name_en': 'Dentistry', 'description_en': 'Dentistry Department - Dental care'},
            'Psychiatry': {'name_en': 'Psychiatry', 'description_en': 'Psychiatry Department - Mental health care'},
        }
        
        # Service translations (Vietnamese name -> English name)
        service_translations = {
            # Nhi khoa (Pediatrics)
            'Khám tổng quát trẻ em': {'name_en': 'Child General Checkup', 'description_en': 'General health examination for children'},
            'Tiêm chủng': {'name_en': 'Vaccination', 'description_en': 'Vaccination services for children'},
            'Tư vấn dinh dưỡng trẻ em': {'name_en': 'Child Nutrition Consultation', 'description_en': 'Nutrition advice for children'},
            'Khám sơ sinh': {'name_en': 'Newborn Checkup', 'description_en': 'Health examination for newborns'},
            'Điều trị nhiễm trùng đường hô hấp': {'name_en': 'Respiratory Infection Treatment', 'description_en': 'Treatment for respiratory tract infections in children'},
            'Tư vấn phát triển trẻ em': {'name_en': 'Child Development Consultation', 'description_en': 'Assessment and advice on child development'},
            'Xét nghiệm máu trẻ em': {'name_en': 'Child Blood Test', 'description_en': 'Regular blood tests for children'},
            'Siêu âm nhi khoa': {'name_en': 'Pediatric Ultrasound', 'description_en': 'Ultrasound diagnostics for children'},
            
            # Tim mạch (Cardiology)
            'Điện tâm đồ (ECG)': {'name_en': 'ECG (Electrocardiogram)', 'description_en': 'Electrocardiogram test'},
            'Siêu âm tim': {'name_en': 'Echocardiography', 'description_en': 'Heart ultrasound'},
            'Xét nghiệm máu tim mạch': {'name_en': 'Cardiovascular Blood Test', 'description_en': 'Blood test for cardiac markers'},
            'Holter ECG 24h': {'name_en': '24h Holter Monitoring', 'description_en': '24-hour heart rhythm monitoring'},
            'Siêu âm Doppler mạch máu': {'name_en': 'Vascular Doppler Ultrasound', 'description_en': 'Doppler ultrasound for blood vessels'},
            'Đo huyết áp liên tục 24h': {'name_en': '24h Blood Pressure Monitoring', 'description_en': '24-hour blood pressure monitoring'},
            'Tư vấn tim mạch': {'name_en': 'Cardiology Consultation', 'description_en': 'Heart disease consultation and prevention'},
            'Test gắng sức': {'name_en': 'Stress Test', 'description_en': 'Cardiac stress testing'},
            
            # Nội tiết (Endocrinology)
            'Xét nghiệm đường huyết': {'name_en': 'Blood Glucose Test', 'description_en': 'Blood sugar testing'},
            'Xét nghiệm hormone': {'name_en': 'Hormone Test', 'description_en': 'Hormone level testing'},
            'Tư vấn dinh dưỡng đái tháo đường': {'name_en': 'Diabetes Nutrition Consultation', 'description_en': 'Nutrition advice for diabetes patients'},
            'Xét nghiệm HbA1c': {'name_en': 'HbA1c Test', 'description_en': 'Long-term blood sugar level test'},
            'Xét nghiệm tuyến giáp': {'name_en': 'Thyroid Function Test', 'description_en': 'Thyroid function testing'},
            'Siêu âm tuyến giáp': {'name_en': 'Thyroid Ultrasound', 'description_en': 'Thyroid ultrasound examination'},
            'Tư vấn quản lý cân nặng': {'name_en': 'Weight Management Consultation', 'description_en': 'Weight loss and management advice'},
            'Xét nghiệm Cortisol': {'name_en': 'Cortisol Test', 'description_en': 'Cortisol hormone testing'},
            
            # Da liễu (Dermatology)
            'Khám da liễu tổng quát': {'name_en': 'General Dermatology Examination', 'description_en': 'General skin examination and consultation'},
            'Điều trị mụn': {'name_en': 'Acne Treatment', 'description_en': 'Acne vulgaris treatment'},
            'Điều trị nám, tàn nhang': {'name_en': 'Melasma & Freckle Treatment', 'description_en': 'Treatment for melasma and freckles'},
            'Điều trị viêm da': {'name_en': 'Dermatitis Treatment', 'description_en': 'Treatment for various types of dermatitis'},
            'Peel da hóa học': {'name_en': 'Chemical Peel', 'description_en': 'Chemical peel skin treatment'},
            'Laser trị sẹo': {'name_en': 'Laser Scar Treatment', 'description_en': 'Laser treatment for scars'},
            'Sinh thiết da': {'name_en': 'Skin Biopsy', 'description_en': 'Biopsy for skin disease diagnosis'},
            'Tư vấn chăm sóc da': {'name_en': 'Skincare Consultation', 'description_en': 'Skincare routine advice'},
            
            # Sản phụ khoa (OB/GYN)
            'Siêu âm thai': {'name_en': 'Prenatal Ultrasound', 'description_en': 'Fetal ultrasound'},
            'Khám phụ khoa': {'name_en': 'Gynecological Examination', 'description_en': 'Regular gynecological checkup'},
            'Xét nghiệm PAP smear': {'name_en': 'PAP Smear Test', 'description_en': 'Cervical cancer screening test'},
            'Siêu âm 4D': {'name_en': '4D Ultrasound', 'description_en': '4D fetal ultrasound'},
            'Xét nghiệm tiền sản': {'name_en': 'Prenatal Testing', 'description_en': 'Comprehensive prenatal test panel'},
            'Đặt vòng tránh thai': {'name_en': 'IUD Insertion', 'description_en': 'Intrauterine device insertion'},
            'Tư vấn kế hoạch hóa gia đình': {'name_en': 'Family Planning Consultation', 'description_en': 'Contraception method consultation'},
            'Khám vô sinh': {'name_en': 'Infertility Examination', 'description_en': 'Infertility examination and consultation'},
            
            # Nội khoa (Internal Medicine)
            'Khám nội khoa tổng quát': {'name_en': 'General Internal Medicine Examination', 'description_en': 'General internal medicine health check'},
            'Xét nghiệm máu tổng quát': {'name_en': 'Complete Blood Count', 'description_en': 'Basic blood test panel'},
            'Điều trị viêm dạ dày': {'name_en': 'Gastritis Treatment', 'description_en': 'Treatment for gastritis and stomach ulcers'},
            'Nội soi dạ dày': {'name_en': 'Gastroscopy', 'description_en': 'Upper GI endoscopy'},
            'Siêu âm ổ bụng': {'name_en': 'Abdominal Ultrasound', 'description_en': 'General abdominal ultrasound'},
            'Điều trị cao huyết áp': {'name_en': 'Hypertension Management', 'description_en': 'Consultation and treatment for high blood pressure'},
            'Xét nghiệm chức năng gan': {'name_en': 'Liver Function Test', 'description_en': 'Liver function assessment'},
            'Xét nghiệm chức năng thận': {'name_en': 'Kidney Function Test', 'description_en': 'Kidney function assessment'},
        }
        
        # Update departments
        dept_updated = 0
        for dept_name, translations in department_translations.items():
            try:
                dept = Department.objects.get(name=dept_name)
                dept.name_en = translations['name_en']
                dept.description_en = translations['description_en']
                dept.save()
                dept_updated += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Updated department: {dept_name} -> {translations["name_en"]}'))
            except Department.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠️ Department not found: {dept_name}'))
        
        # Update services
        svc_updated = 0
        for svc_name, translations in service_translations.items():
            try:
                services = Service.objects.filter(name=svc_name)
                for svc in services:
                    svc.name_en = translations['name_en']
                    svc.description_en = translations['description_en']
                    svc.save()
                    svc_updated += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Updated service: {svc_name} -> {translations["name_en"]}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️ Error updating service {svc_name}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Localization update completed!'))
        self.stdout.write(self.style.SUCCESS(f'   Departments updated: {dept_updated}'))
        self.stdout.write(self.style.SUCCESS(f'   Services updated: {svc_updated}'))
