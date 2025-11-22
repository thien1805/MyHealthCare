# Postman Testing Guide - MyHealthCare API

## Setup

1. **Import Collection**: Import file `postman_collection.json` vào Postman
2. **Set Base URL**: Collection variable `base_url` mặc định là `http://localhost:8000/api/v1`
   - Nếu server chạy ở port khác, sửa variable này

## Testing Flow

### 1. Setup Test Data

Trước khi test, cần chạy seed data:

```bash
# Seed users (admin, doctors, patients)
python manage.py seed_data

# Seed departments, services, rooms
python manage.py seed_departments
```

### 2. Authentication Flow

#### Step 1: Register Patient
- **Request**: `POST /register/`
- **Body**: 
  ```json
  {
    "email": "patient1@test.com",
    "password": "patient123",
    "full_name": "Nguyễn Văn A",
    "phone_num": "0901234567",
    "role": "patient",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "address": "123 Đường ABC, Quận 1, TP.HCM"
  }
  ```

#### Step 2: Login
- **Request**: `POST /token/`
- **Body**:
  ```json
  {
    "email": "patient1@test.com",
    "password": "patient123"
  }
  ```
- **Response**: Sẽ tự động lưu `access_token`, `refresh_token`, và `patient_id` vào collection variables

#### Step 3: Get Profile
- **Request**: `GET /profile/`
- **Headers**: `Authorization: Bearer {{access_token}}`

### 3. Browse Departments & Doctors

#### List Departments (Specialties)
- **Request**: `GET /services/specialties/`
- **Response**: Danh sách các khoa (Nhi khoa, Tim mạch, Nội tiết, Da liễu, Sản phụ khoa)
- **Note**: Lưu `department_id` từ response để dùng cho booking

#### List Doctors
- **Request**: `GET /doctors/`
- **Optional Filter**: `GET /doctors/?specialization=Nhi khoa`
- **Note**: Lưu `doctor_id` từ response để dùng cho booking

#### List Services
- **Request**: `GET /services/`
- **Optional Filter**: `GET /services/?department=Nhi khoa`
- **Note**: Lưu `service_id` từ response để dùng cho assign service (doctor)

### 4. Check Available Slots

- **Request**: `GET /available-slots/?doctor_id={{doctor_id}}&date=2025-12-01&department_id={{department_id}}`
- **Response**: Danh sách các time slots (08:00 - 16:30) với trạng thái available/not available
- **Note**: Chọn một time slot available để booking

### 5. Book Appointment (Patient)

- **Request**: `POST /appointments/`
- **Headers**: `Authorization: Bearer {{access_token}}`
- **Body**:
  ```json
  {
    "doctor_id": 2,
    "department_id": 1,
    "appointment_date": "2025-12-01",
    "appointment_time": "09:00",
    "symptoms": "Sốt, ho, sổ mũi",
    "reason": "Khám bệnh cho trẻ em",
    "notes": "Trẻ 5 tuổi, sốt 3 ngày"
  }
  ```
- **Response**: 
  - `appointment_id` sẽ tự động lưu vào collection variable
  - `estimated_fee` = `health_examination_fee` (chỉ phí thăm khám, chưa có service)
  - `service` = `null`

### 6. View Appointments

- **Request**: `GET /appointments/my-appointments/`
- **Optional Filters**:
  - `?status=booked` - Lọc theo status
  - `?date_from=2025-12-01&date_to=2025-12-31` - Lọc theo khoảng thời gian

### 7. Assign Service (Doctor Only)

**Lưu ý**: Cần login với tài khoản doctor để test API này.

- **Request**: `POST /appointments/{{appointment_id}}/assign-service/`
- **Headers**: `Authorization: Bearer {{access_token}}` (doctor token)
- **Body**:
  ```json
  {
    "service_id": 1
  }
  ```
- **Response**: 
  - `estimated_fee` = `health_examination_fee + service.price` (phí thăm khám + phí dịch vụ)
  - `service` = service object đã được assign

### 8. Cancel Appointment

- **Request**: `POST /appointments/{{appointment_id}}/cancel/`
- **Headers**: `Authorization: Bearer {{access_token}}`
- **Body**:
  ```json
  {
    "reason": "Không thể đến được"
  }
  ```
- **Business Rule**: Phải cancel trước 24 giờ

### 9. Reschedule Appointment

- **Request**: `PUT /appointments/{{appointment_id}}/reschedule/`
- **Headers**: `Authorization: Bearer {{access_token}}`
- **Body**:
  ```json
  {
    "new_date": "2025-12-02",
    "new_time": "10:00",
    "reason": "Có việc đột xuất"
  }
  ```

## Test Scenarios

### Scenario 1: Complete Booking Flow (Patient)
1. Login as patient
2. List departments → Chọn department
3. List doctors → Chọn doctor
4. Get available slots → Chọn time slot
5. Book appointment → Verify `estimated_fee` = `health_examination_fee` only
6. View my appointments → Verify appointment created

### Scenario 2: Doctor Assign Service
1. Login as doctor
2. Get appointment by ID
3. Assign service → Verify `estimated_fee` = `health_examination_fee + service.price`
4. Get appointment again → Verify service assigned

### Scenario 3: Cancel & Reschedule
1. Login as patient
2. Book appointment
3. Cancel appointment (with reason)
4. Book new appointment
5. Reschedule appointment

## Collection Variables

Các variables sẽ tự động được set khi chạy requests:
- `access_token`: JWT access token (tự động set sau login)
- `refresh_token`: JWT refresh token (tự động set sau login)
- `patient_id`: ID của patient (tự động set sau login patient)
- `doctor_id`: ID của doctor (tự động set sau login doctor)
- `appointment_id`: ID của appointment (tự động set sau book appointment)
- `department_id`: ID của department (có thể set thủ công hoặc từ response)
- `service_id`: ID của service (có thể set thủ công hoặc từ response)

## Common Issues

1. **401 Unauthorized**: 
   - Kiểm tra `access_token` có hợp lệ không
   - Token có thể đã hết hạn, cần refresh hoặc login lại

2. **403 Forbidden**: 
   - Kiểm tra role của user (patient/doctor/admin)
   - Một số API chỉ dành cho patient hoặc doctor

3. **400 Bad Request**: 
   - Kiểm tra request body format
   - Kiểm tra các business rules (ví dụ: cancel trước 24h)

4. **404 Not Found**: 
   - Kiểm tra ID có tồn tại không
   - Kiểm tra URL path có đúng không

## Notes

- Tất cả dates phải ở format `YYYY-MM-DD`
- Tất cả times phải ở format `HH:MM` (24-hour format)
- Time slots: 08:00 - 16:30, mỗi slot 30 phút
- `estimated_fee` khi booking = `health_examination_fee` (chỉ phí thăm khám)
- `estimated_fee` sau khi assign service = `health_examination_fee + service.price`

