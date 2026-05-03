# MyHealthCare Backend

Backend API for the MyHealthCare appointment platform.

## 🚀 Demo-ready features

- Demo login endpoint: `POST /api/v1/auth/demo-login/`
- Demo account credentials: `demo@myhealthcare.com / demo123`
- Standard login endpoint: `POST /api/v1/auth/login/`
- API docs / Swagger: `GET /api/v1/docs/`
- OpenAPI schema: `GET /api/v1/schema/`

## ✅ Quick start

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run database migrations:
   ```bash
   python manage.py migrate
   ```
4. Seed sample data, including demo account and sample users:
   ```bash
   python manage.py seed_full_data
   ```
5. Start the backend server:
   ```bash
   python manage.py runserver
   ```

## 🔐 Authentication

### Demo login

Use this endpoint to generate a ready-to-use demo patient token:

- `POST /api/v1/auth/demo-login/`

Response includes JWT tokens for quick API testing.

### Standard login

- `POST /api/v1/auth/login/`
- Body:
  ```json
  {
    "email": "demo@myhealthcare.com",
    "password": "demo123"
  }
  ```

### Demo account credentials

- Email: `demo@myhealthcare.com`
- Password: `demo123`

## 📄 API documentation

After running the server locally, open the interactive docs at:

- `http://127.0.0.1:8000/api/v1/docs/`

This is ideal for recruiters to explore backend endpoints and test them directly.

## 🌐 Deploy notes

This repository is a Django REST backend. If you deploy a frontend on Vercel, connect it to this backend URL via your frontend environment variables.

### CORS and Vercel

To allow a Vercel-hosted frontend to call this API, set the backend environment variable:

- `CORS_ALLOW_ALL_ORIGINS=True`

or add the Vercel domain to `CORS_ALLOWED_ORIGINS` in `myhealthcare/settings.py`.

## 🧪 Seed data included

The seed command creates:

- Admin: `admin@myhealthcare.com / admin123`
- Demo user: `demo@myhealthcare.com / demo123`
- Sample doctor accounts
- Sample patient accounts

## 💡 Notes for portfolio

- Use the demo account for quick frontend/back-end flow testing.
- Share the Swagger docs URL to let reviewers inspect API routes.
- If you deploy a separate front-end, put the backend URL in the frontend config.
