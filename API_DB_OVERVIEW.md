# MyHealthCare – Database & API Overview

_Last updated: 2025-12-06_

## Database schema (Django models)

### Accounts
- **User** (`users`)
  - `email` (unique), `full_name`, `phone_num`, `role` (`admin|doctor|patient`), `is_active`, `is_staff`, timestamps.
- **Patient** (`patients`)
  - `user` (1-1 User), `date_of_birth`, `gender` (`male|female|other`), `address`, `insurance_id`, `emergency_contact`, `emergency_contact_phone` (10 digits), `created_at`.
- **Doctor** (`doctors`)
  - `user` (1-1 User), `department` (FK Department, PROTECT), `room` (1-1 Room, nullable), `title`, `specialization`, `license_number` (unique), `experience_years`, `consultation_fee`, `bio`, `rating`, `avatar_url`, `total_reviews`, `created_at`.

### Appointments
- **Department** (`departments`)
  - `name` (unique), `icon`, `description`, `is_active`, `health_examination_fee`, timestamps.
- **Service** (`services`)
  - `department` (FK Department), `name`, `description`, `price`, `is_active`, `created_at`.
- **Room** (`rooms`)
  - `room_number` (unique), `floor`, `department` (FK Department, nullable), `is_active`, `created_at`.
- **Appointment** (`appointments`)
  - `patient` (FK User, role=patient), `doctor` (FK User, role=doctor), `department` (FK Department, PROTECT), `service` (FK Service, nullable), `appointment_date`, `appointment_time` (choices 08:00–16:30, 30m step), `room` (FK Room, nullable), `status` (`booked|confirmed|completed|cancelled`), `symptoms`, `reason`, `notes`, `estimated_fee`, `cancellation_reason`, `cancelled_at`, `rescheduled_from` (JSON), timestamps. Indexed by date/time, doctor, patient, department.
- **MedicalRecord** (`medical_records`)
  - `appointment` (1-1 Appointment), `diagnosis`, `prescription`, `treatment_plan`, `notes`, `follow_up_date`, `vital_signs` (JSON), `created_by` (FK User doctor, nullable), timestamps. Indexed by appointment and created_by.

### Core
- Currently empty (`apps/core/models.py`).

### Key relationships
- User 1-1 Patient; User 1-1 Doctor.
- Doctor ↔ Department (many doctors per department), Doctor ↔ Room (1-1 optional).
- Appointment links Patient (User), Doctor (User), Department; optionally Service and Room.
- MedicalRecord 1-1 Appointment.
- Department has many Services and Rooms.

## API surface (mounted under `/api/v1/`)

### Auth & Accounts
- `POST /auth/register/` — register user.
- `POST /auth/login/` — login, returns tokens.
- `POST /auth/logout/` — logout current session.
- `POST /auth/logout-all/` — logout all sessions.
- `POST /auth/forgot-password/` — request reset (validates email exists; sends link).
- `POST /auth/verify-reset-token/` — verify reset token.
- `POST /auth/reset-password/` — reset password with uid+token.
- `GET /user/me/` — get current user profile (includes nested patient/doctor profile by role).
- `PUT/PATCH /user/me/` — update profile. Patient can update `full_name, phone_num` + patient_profile fields; Doctor can update `full_name, phone_num` + doctor_profile fields. (Current serializer allows broader doctor fields; recent requirement is to limit to room/title/specialization/bio.)
- `GET /doctors/` — public list of doctors; filter by `department_id` or `specialization`.

### JWT helpers
- `POST /token/` — obtain access & refresh.
- `POST /token/refresh/` — refresh access token.

### Departments & Services (read-only)
- `GET /departments/` — list active departments (paginated).
- `GET /departments/{id}/` — department detail (includes services/doctors via serializer).
- `GET /services/` — list active services; filter by `department_id` or `specialty_id`.
- `GET /services/{id}/` — service detail.
- `GET /services/specialties/` — list unique specialties/departments (alias helper).

### Appointments
- `GET /appointments/available-slots/?doctor_id=&date=` — public; returns all 30m slots with availability, optional `department_id`.
- `GET /appointments/` — role-based list (patient: own; doctor: own; admin: all). Query: `status`, `date_from`, `date_to`, paging.
- `POST /appointments/` — patient books appointment; department fee used; room auto-assigned (doctor’s room else first active room in department); service left null until doctor assigns.
- `GET /appointments/{id}/` — retrieve (permissions based on role/ownership).
- `PUT/PATCH /appointments/{id}/` — update (role restrictions apply in code logic).
- `DELETE /appointments/{id}/` — delete/cancel (if allowed).
- `GET /appointments/doctors-by-department/?department_id=` — auth; list doctors for a department (helper for forms).
- Additional actions inside viewset include cancel/reschedule/assign-service/complete (see `apps/appointments/views.py` for exact business rules and status transitions).

### Medical Records
- Exposed via AppointmentViewSet actions (create/update medical record for an appointment; doctor-only). See `MedicalRecordSerializer` usages in `apps/appointments/views.py`.

### Documentation
- `GET /api/v1/schema/` — OpenAPI schema.
- `GET /api/v1/docs/` — Swagger UI.
- `GET /api/v1/redoc/` — Redoc UI.

## Notes
- Base URL prefix is `/api/v1/` (see `myhealthcare/urls.py`).
- CORS/HTTPS/ALLOWED_HOSTS depend on settings/env; dev typically uses `DEBUG=True`.
- Rooms and departments must exist to auto-assign rooms when booking appointments.
- Password reset links use `FRONTEND_URL` in settings/env.
