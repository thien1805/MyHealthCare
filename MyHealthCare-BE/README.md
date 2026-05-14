## MyHealthCare Backend

Backend nay la Django API. Repo da duoc chinh de:

- chay local khong can Azure
- mac dinh dung SQLite neu chua cau hinh Postgres
- deploy len Render bang Python service

## Chay local tren Windows PowerShell

1. Tao va kich hoat virtual environment

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Cai dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Tao `.env` neu muon custom env

```powershell
Copy-Item .env.example .env
```

Noi dung local toi thieu:

```env
DJANGO_SECRET_KEY=dev-only-change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173
```

4. Chay migrate va run server

```powershell
python manage.py migrate
python manage.py runserver
```

Neu ban khong set DB gi, local se tu dung `db.sqlite3`.

Neu muon dung Postgres local, set mot trong hai cach:

- `DATABASE_URL=postgresql://user:password@localhost:5432/dbname`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`

## Deploy len Render

Repo da co `render.yaml`, `build.sh`, va `startup.sh`.

1. Push repo len GitHub
2. Tren Render, chon `New +` -> `Blueprint`
3. Ket noi repo nay
4. Bo sung env vars trong dashboard neu can:

```env
FRONTEND_URL=https://your-frontend-domain
CORS_ALLOWED_ORIGINS=https://your-frontend-domain
PUBLIC_API_URL=https://your-api-domain.onrender.com
DJANGO_DEBUG=False
```

`DJANGO_SECRET_KEY` se duoc Render sinh tu dong. `DATABASE_URL` duoc noi tu Render Postgres trong `render.yaml`.

## Render commands

- Build command: `bash build.sh`
- Start command: `bash startup.sh`

`build.sh` cai dependencies va collect static. `startup.sh` chay migrations roi start Gunicorn voi `PORT` cua Render.

## Ve package.json

Backend nay la Python/Django. `package.json` va `package-lock.json` khong duoc dung de chay API.

Neu Render detect nham thanh Node service thi:

- dung `Blueprint` voi `render.yaml` de ep `env: python`
- hoac xoa `package.json` neu file do khong can cho workflow cua ban
