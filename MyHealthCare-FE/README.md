<div align="center">
  <img src="src/assets/UIT-logo.png" alt="University Logo" width="400" />
</div>

<br />

<div align="center">
  <h1>Web Application Development Project</h1> 
  <h2>MyHealthCare</h2>
</div>

<br />

## Team Members

| No. | Student ID | Full Name |
| :---: | :---: | :--- |
| 1 | 23521485 | Phạm Ngọc Thiện |
| 2 | 23521111 | Nguyễn Thị Quỳnh Nhi |

<br />

## Project Description

**MyHealthCare** is a web-based healthcare management system designed to streamline the interaction between patients, doctors, and hospital administrators. Developed as part of the Web Application Development course at **University of Information Technology (VNUHCM-UIT)**, the project focuses on delivering a seamless user experience for booking medical appointments and managing health records.

The application addresses common challenges in healthcare scheduling by providing:
- **Patients** with an easy way to type symptom to find specialty (if patient don't know), choose doctors, view schedules, and book appointments without flexible time slots, AI chatbot for health assistant (a AI consultant but not a doctor).
- **Doctors** with tools to manage their daily schedules, view patient histories, and digitalize medical records.
- **Administrators** with a robust dashboard to oversee system operations (using Django administration), departments, and user roles.

## Key Functions

### For Patients
*   **Account Management**: Secure registration, login (JWT), and profile updates.
*   **Doctor Discovery**: Browse doctors by department, specialization, or rating.
*   **Appointment Booking**: Real-time checking of doctor availability and slot booking.
*   **History & Status**: Track appointment status (Pending, Confirmed, Completed, Cancelled).
*   **Health Assistant**: AI chatbot for health assistant (a AI consultant but not a doctor).

### For Doctors
*   **Dashboard**: Overview of upcoming appointments and daily schedule.
*   **Patient Management**: Access to patient details and appointment context.
*   **Electronic Medical Records**: Create and update medical records, including diagnosis, treatment plans, and prescriptions.
*   **Schedule Control**: Manage availability and working hours.

### System Features (Core)
*   **Department Management**: Organization of checking departments and services.
*   **Room Allocation**: Automated or manual assignment of consultation rooms.
*   **Notifications**: (Planned) System notifications for appointment updates.

## Technologies Used

The project is built using a modern, scalable tech stack ensuring high performance and maintainability.

### Frontend
Used for building the responsive user interface.
*   **Framework**: [React 19](https://react.dev/)
*   **Build Tool**: [Vite](https://vitejs.dev/)
*   **Styling**: [TailwindCSS](https://tailwindcss.com/) & PostCSS
*   **Routing**: React Router DOM v7
*   **State Management & API**: Axios, React Hooks
*   **Icons**: Lucide React

### Backend
Robust API service handling data logic and security.
*   **Language**: Python
*   **Framework**: [Django 5](https://www.djangoproject.com/)
*   **API Toolkit**: Django REST Framework (DRF)
*   **Database**: PostgreSQL (via `psycopg2`)
*   **Authentication**: Simple JWT (JSON Web Tokens)
*   **Documentation**: Swagger / Redoc (via `drf-spectacular`)
*   **AI Integration**: OpenRouter API (Unified API Key Platform for Open Source AI)

### Tools & DevOps
*   **Version Control**: Git & GitHub
*   **Testing**: Pytest (Backend), Postman
*   **Containerization**: (Optional/Planned) Docker
*   **Deployment**: Vercel, Azure App Service, Azure Virtual Machine (Turned off the resource for now to save cost and avoid being charged)

---

### How to Run Locally

#### 1. Backend (Django)
```bash
# Navigate to backend directory
cd MyHealthCare

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

#### 2. Frontend (React)
```bash
# Navigate to frontend directory
cd WebProject-FE

# Install dependencies
npm install

# Start development server
npm run dev
```

--- 
## Resources and Product Website
*   **Link API Documentation**: https://myhealthcare-api-h3amhrevg2feeab9.southeastasia-01.azurewebsites.net/api/v1/docs
*   **Link Product**: https://myhealthcare-two.vercel.app/
*   **Link Github BE**: https://github.com/thien1805/MyHealthCare
*   **Link Github FE**: https://github.com/quinnie-o3/WebProject-FE
*   **Link Video Demo**: https://youtu.be/q92VsG7hyGI?feature=shared

---
*A course project of Web Application Development - UIT.*
