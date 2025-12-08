# MyHealthCare – API Documentation

_Last updated: 2025-12-09_

> **API Base URL:** `https://myhealthcare-api.azurewebsites.net/api/v1/`  
> **Swagger Docs:** `/api/v1/docs/`  
> **ReDoc:** `/api/v1/redoc/`

---

## 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register new user |
| POST | `/auth/login/` | Login, returns access & refresh tokens |
| POST | `/auth/logout/` | Logout current session |
| POST | `/auth/logout-all/` | Logout all sessions |
| POST | `/auth/forgot-password/` | Request password reset email |
| POST | `/auth/verify-reset-token/` | Verify reset token validity |
| POST | `/auth/reset-password/` | Reset password with uid+token |
| POST | `/token/` | Obtain JWT access & refresh tokens |
| POST | `/token/refresh/` | Refresh access token |

### Login Request
```json
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "your_password"
}
```

### Login Response
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "role": "patient"
  },
  "tokens": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
}
```

---

## 👤 User Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/me/` | Get current user profile |
| PUT/PATCH | `/user/me/` | Update profile |
| GET | `/doctors/` | List all doctors (public) |

### Profile Response
```json
{
  "id": 1,
  "email": "patient@example.com",
  "full_name": "Nguyen Van A",
  "phone_num": "0901234567",
  "role": "patient",
  "patient_profile": {
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "address": "123 ABC Street",
    "insurance_id": "SV123456"
  }
}
```

---

## 🏥 Departments & Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/departments/` | List all active departments |
| GET | `/departments/{id}/` | Department detail with doctors |
| GET | `/services/` | List services, filter by `?department_id=` |
| GET | `/services/{id}/` | Service detail |

### Department Response
```json
{
  "id": 1,
  "name": "Khoa Nội tổng hợp",
  "name_en": "Internal Medicine",
  "icon": "🩺",
  "description": "Khám và điều trị các bệnh nội khoa",
  "description_en": "Internal medicine examination",
  "health_examination_fee": "200000.00",
  "is_active": true
}
```

---

## 📅 Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/appointments/available-slots/` | Get available time slots |
| GET | `/appointments/doctors-by-department/` | Doctors in a department |
| POST | `/appointments/` | Book new appointment |
| GET | `/appointments/` | List appointments (role-based) |
| GET | `/appointments/{id}/` | Appointment detail |
| POST | `/appointments/{id}/cancel/` | Cancel appointment |
| PUT | `/appointments/{id}/reschedule/` | Reschedule appointment |
| PATCH | `/appointments/{id}/update-status/` | Update status (doctor) |
| POST | `/appointments/{id}/assign-service/` | Assign service (doctor) |
| POST | `/appointments/{id}/medical-record/` | Create medical record (doctor) |
| POST | `/appointments/{id}/pay/` | Mark as paid |

### Available Slots Request
```
GET /api/v1/appointments/available-slots/?doctor_id=1&date=2025-12-15&department_id=1
```

### Available Slots Response
```json
{
  "date": "2025-12-15",
  "doctor": {
    "id": 1,
    "full_name": "BS. Nguyen Van B",
    "specialization": "Nội tổng hợp"
  },
  "available_slots": [
    {"time": "08:00", "available": true, "room": "101"},
    {"time": "08:30", "available": false, "room": "101"},
    {"time": "09:00", "available": true, "room": "101"}
  ]
}
```

### Book Appointment Request
```json
POST /api/v1/appointments/
{
  "doctor_id": 1,
  "department_id": 1,
  "appointment_date": "2025-12-15",
  "appointment_time": "09:00:00",
  "symptoms": "Đau đầu, sốt nhẹ",
  "reason": "Khám tổng quát",
  "notes": ""
}
```

### Appointment Response
```json
{
  "id": 1,
  "patient": {"id": 2, "full_name": "Nguyen Van A"},
  "doctor": {"id": 1, "full_name": "BS. Nguyen Van B"},
  "department": {"id": 1, "name": "Khoa Nội tổng hợp"},
  "service": null,
  "appointment_date": "2025-12-15",
  "appointment_time": "09:00:00",
  "status": "upcoming",
  "symptoms": "Đau đầu, sốt nhẹ",
  "estimated_fee": "200000.00",
  "room": {"room_number": "101", "floor": 1},
  "medical_record": null
}
```

---

## 👨‍⚕️ Role-Based Endpoints

### Patient Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patient/appointments/` | Patient's appointments (paginated) |

### Doctor Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/appointments/` | Doctor's appointments (paginated) |

---

## 🤖 AI Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/appointments/suggest-department/` | AI suggests department from symptoms |
| POST | `/ai/health-qa/` | AI health chatbot |

### Suggest Department Request
```json
POST /api/v1/appointments/suggest-department/
{
  "symptoms": "Tôi bị đau đầu và chóng mặt"
}
```

### Suggest Department Response
```json
{
  "primary_department": "Khoa Nội tổng hợp",
  "reason": "Triệu chứng đau đầu và chóng mặt cần được khám nội khoa",
  "urgency": "medium"
}
```

### Health Chatbot Request
```json
POST /api/v1/ai/health-qa/
{
  "message": "Cảm cúm có nguy hiểm không?",
  "conversation_history": []
}
```

---

## 📊 Database Models

### User
- `email` (unique), `full_name`, `phone_num`
- `role`: `admin` | `doctor` | `patient`
- `is_active`, `is_staff`, timestamps

### Patient (extends User)
- `date_of_birth`, `gender`, `address`
- `insurance_id`, `emergency_contact`, `emergency_contact_phone`

### Doctor (extends User)
- `department` (FK), `room` (FK), `title`, `specialization`
- `license_number`, `experience_years`, `consultation_fee`
- `bio`, `rating`, `avatar_url`

### Department
- `name`, `name_en`, `icon`, `description`, `description_en`
- `health_examination_fee`, `is_active`

### Service
- `department` (FK), `name`, `name_en`
- `description`, `description_en`, `price`, `is_active`

### Appointment
- `patient` (FK User), `doctor` (FK User), `department` (FK)
- `service` (FK, optional), `room` (FK, optional)
- `appointment_date`, `appointment_time`
- `status`: `upcoming` | `confirmed` | `completed` | `cancelled`
- `symptoms`, `reason`, `notes`, `estimated_fee`

### MedicalRecord
- `appointment` (1-1), `diagnosis`, `prescription`
- `treatment_plan`, `notes`, `follow_up_date`
- `vital_signs` (JSON), `created_by` (FK doctor)

---

## 🔒 Authorization

- **Bearer Token**: Include in header `Authorization: Bearer <access_token>`
- **Role-based**: Some endpoints restricted by role
- **Ownership**: Patients only see their own data

## ⚠️ Error Responses

```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

Common HTTP status codes:
- `400` Bad Request
- `401` Unauthorized  
- `403` Forbidden
- `404` Not Found
- `500` Server Error

---

## 🌐 CORS & Environment

- CORS enabled for frontend domains
- Environment variables:
  - `OPENROUTER_API_KEY` - AI service
  - `FRONTEND_URL` - For password reset links
  - `DATABASE_URL` - PostgreSQL connection
