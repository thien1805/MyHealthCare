# 🚀 Hướng Dẫn Deploy Django lên Azure App Service

## 📋 Mục Lục
1. [Chuẩn Bị](#chuẩn-bị)
2. [Tạo Azure PostgreSQL Database](#bước-1-tạo-postgresql-database)
3. [Tạo Azure Web App](#bước-2-tạo-azure-web-app)  
4. [Cấu Hình Environment Variables](#bước-3-cấu-hình-environment-variables)
5. [Deploy Code](#bước-4-deploy-code)
6. [Kiểm Tra và Test](#bước-5-kiểm-tra-và-test)
7. [Troubleshooting](#troubleshooting)

---

## Chuẩn Bị

### Yêu Cầu
- Tài khoản Azure (miễn phí hoặc trả phí)
- Code đã được push lên GitHub
- Azure CLI đã cài đặt (tùy chọn)

### Cấu Trúc Project

Project đã được cấu trúc sẵn để deploy lên Azure:

```
MyHealthCare/
├── manage.py              # Django management
├── myhealthcare/          # Django settings
├── apps/                  # Django apps
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version (3.11.9)
├── startup.sh            # Azure startup script
├── .deployment           # Azure deployment config
└── pytest.ini            # Test configuration
```

---

## Bước 1: Tạo PostgreSQL Database

### 1.1. Vào Azure Portal

1. Truy cập: https://portal.azure.com
2. Đăng nhập tài khoản

### 1.2. Tạo Resource Group

1. Search bar → nhập "Resource groups"
2. Click **"+ Create"**
3. Điền thông tin:
   - **Subscription**: Chọn subscription của bạn
   - **Resource group name**: `myhealthcare-rg`
   - **Region**: `Southeast Asia` hoặc `East Asia`
4. Click **"Review + create"** → **"Create"**

### 1.3. Tạo PostgreSQL Server

1. Search bar → nhập "Azure Database for PostgreSQL"
2. Click **"+ Create"**
3. Chọn **"Flexible server"** → Click **"Create"**

**Tab Basics:**
- **Resource group**: `myhealthcare-rg`
- **Server name**: `myhealthcare-db-server` (phải unique)
- **Region**: `Southeast Asia`
- **PostgreSQL version**: `14`
- **Workload type**: `Development` (rẻ nhất)
- **Compute + storage**: Click "Configure" → Chọn **Burstable B1ms** (~$12/tháng)

**Authentication:**
- **Authentication method**: `PostgreSQL authentication`
- **Admin username**: `myadmin`
- **Password**: `MyHealthCare2024!` (LƯU LẠI PASSWORD NÀY!)
- **Confirm password**: `MyHealthCare2024!`

Click **"Next: Networking >"**

**Tab Networking:**
- **Connectivity method**: ✅ `Public access (allowed IP addresses)`
- Click **"+ Add 0.0.0.0 - 255.255.255.255"** (Allow Azure services)
- ✅ Check: `Allow public access from any Azure service within Azure to this server`

Click **"Review + create"** → **"Create"**

⏰ **Đợi 5-10 phút**

### 1.4. Tạo Database

Sau khi server tạo xong:

1. Vào resource **myhealthcare-db-server**
2. Menu bên trái → **"Databases"**
3. Click **"+ Add"**
4. **Database name**: `myhealthcare`
5. Click **"Save"**

### 1.5. Lấy Connection String

1. Vào **myhealthcare-db-server**
2. Menu trái → **"Connection strings"**
3. Copy connection string, format:

```
postgresql://myadmin:MyHealthCare2024!@myhealthcare-db-server.postgres.database.azure.com:5432/myhealthcare?sslmode=require
```

✅ **LƯU LẠI CONNECTION STRING NÀY!**

---

## Bước 2: Tạo Azure Web App

### 2.1. Tạo App Service Plan

1. Search bar → nhập "App Service plans"
2. Click **"+ Create"**
3. Điền thông tin:
   - **Resource Group**: `myhealthcare-rg`
   - **Name**: `myhealthcare-plan`
   - **Operating System**: **Linux**
   - **Region**: `Southeast Asia`
   - **Pricing tier**: Click "Explore pricing plans"
     - **Development**: Free F1 ($0) - test only
     - **Production**: Basic B1 (~$13/tháng) - khuyên dùng
4. Click **"Review + create"** → **"Create"**

### 2.2. Tạo Web App

1. Search bar → nhập "App Services"
2. Click **"+ Create"** → **"Web App"**

**Tab Basics:**
- **Resource Group**: `myhealthcare-rg`
- **Name**: `myhealthcare-api-2024` (PHẢI UNIQUE, đổi năm nếu trùng)
- **Publish**: ⭕ `Code`
- **Runtime stack**: `Python 3.11`
- **Operating System**: `Linux`
- **Region**: `Southeast Asia`
- **App Service Plan**: Chọn `myhealthcare-plan` đã tạo

Click **"Review + create"** → **"Create"**

⏰ **Đợi 2-3 phút**

---

## Bước 3: Cấu Hình Environment Variables

### 3.1. Generate SECRET_KEY

Mở terminal local và chạy:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy kết quả (ví dụ: `django-insecure-abc123xyz...`)

### 3.2. Set Application Settings

1. Vào Web App **myhealthcare-api-2024**
2. Menu trái → **"Configuration"** (trong Settings)
3. Tab **"Application settings"**
4. Click **"+ New application setting"** để thêm từng biến:

| Name | Value | Ghi chú |
|------|-------|---------|
| `DJANGO_SECRET_KEY` | (secret key từ step 3.1) | Bắt buộc |
| `DJANGO_DEBUG` | `False` | Bắt buộc |
| `DJANGO_ALLOWED_HOSTS` | `myhealthcare-api-2024.azurewebsites.net` | Đổi tên app cho đúng |
| `AZURE_POSTGRESQL_CONNECTIONSTRING` | (từ Bước 1.5) | Bắt buộc |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Bắt buộc |

**Sau khi thêm hết** → Click **"Save"** (ở trên cùng) → Click **"Continue"**

### 3.3. Set Startup Command

1. Vẫn ở trang **Configuration**
2. Tab **"General settings"**
3. Kéo xuống tìm **"Startup Command"**
4. Nhập:

```bash
python manage.py migrate --no-input && python manage.py collectstatic --no-input --clear && gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 --access-logfile=- --error-logfile=- myhealthcare.wsgi:application
```

5. Click **"Save"** → **"Continue"**

---

## Bước 4: Deploy Code

### Option A: Deploy từ GitHub (Khuyên dùng)

#### 4.1. Connect GitHub

1. Menu trái → **"Deployment Center"**
2. **Source**: Chọn `GitHub`
3. Click **"Authorize"** → Login GitHub nếu cần
4. Chọn:
   - **Organization**: Tài khoản GitHub của bạn
   - **Repository**: `MyHealthCare`
   - **Branch**: `main` hoặc `feature/accounts-api`
5. Click **"Save"**

✅ **Azure sẽ tự động setup GitHub Actions và deploy!**

#### 4.2. Xem Deploy Progress

1. Vào GitHub repo
2. Tab **"Actions"**
3. Xem workflow đang chạy
4. Đợi đến khi có dấu ✅ xanh (5-10 phút)

### Option B: Deploy từ Local Git

#### 4.1. Get Deployment Credentials

1. **Deployment Center** → Chọn **"Local Git"**
2. Click **"Save"**
3. Vào tab **"Local Git/FTPS credentials"**
4. Copy **"Git Clone Uri"**

#### 4.2. Push từ Local

Terminal local:

```bash
cd /Users/thien2005/Workspace/PROJECT/MyHealthCare

# Add Azure remote
git remote add azure <Git-Clone-Uri-from-step-4.1>

# Push
git push azure main
```

---

## Bước 5: Kiểm Tra và Test

### 5.1. Enable Logging

1. Menu trái → **"App Service logs"**
2. Bật:
   - **Application logging**: `File System` → Level: `Verbose`
   - **Web server logging**: `File System`
   - **Detailed error messages**: `On`
   - **Failed request tracing**: `On`
3. Click **"Save"**

### 5.2. Xem Logs

1. Menu trái → **"Log stream"**
2. Đợi 10-20 giây
3. Xem logs, tìm:

```
✅ Operations to perform...
✅ Running migrations...
✅ XX static files copied...
✅ [INFO] Starting gunicorn 21.2.0
✅ [INFO] Listening at: http://0.0.0.0:8000
```

Nếu thấy các dòng trên → **DEPLOY THÀNH CÔNG!**

### 5.3. Restart App

1. Tab **"Overview"**
2. Click **"Restart"** (button ở trên)
3. Click **"Yes"**
4. Đợi 1 phút

### 5.4. Test API

Mở browser hoặc Postman:

**1. Test Admin:**
```
https://myhealthcare-api-2024.azurewebsites.net/api/v1/admin/
```
→ Phải thấy Django admin login page

**2. Test API Endpoint:**
```
https://myhealthcare-api-2024.azurewebsites.net/api/v1/auth/register/
```
→ Phải thấy API form

**3. Test Register API:**

Method: `POST`
URL: `https://myhealthcare-api-2024.azurewebsites.net/api/v1/auth/register/`
Headers: `Content-Type: application/json`
Body:
```json
{
  "email": "test@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "full_name": "Test User",
  "phone_num": "0901234567",
  "role": "patient",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "address": "123 Test St"
}
```

Expected: Status **201 Created**

---

## Troubleshooting

### ❌ Vấn Đề 1: "Application Error" hoặc 500

**Nguyên nhân:**
- Environment variables sai
- Database connection failed
- Startup command sai

**Cách fix:**

1. **Check Logs:**
   - Log stream → Tìm dòng ERROR
   
2. **Verify Environment Variables:**
   - Configuration → Application settings
   - Đảm bảo có đủ 5 settings
   
3. **Test Database Connection:**
   - SSH → `python manage.py dbshell`

### ❌ Vấn Đề 2: "502 Bad Gateway"

**Nguyên nhân:** Gunicorn không start

**Cách fix:**

1. Check startup command
2. Xem logs: có thể thiếu dependencies
3. Verify requirements.txt có đủ packages

### ❌ Vấn Đề 3: "DisallowedHost at /"

**Nguyên nhân:** `ALLOWED_HOSTS` sai

**Cách fix:**

1. Configuration → Application settings
2. Edit `DJANGO_ALLOWED_HOSTS`
3. Value phải match: `<your-app-name>.azurewebsites.net`
4. Save → Restart

### ❌ Vấn Đề 4: Database connection error

**Check connection string format:**

```
postgresql://USERNAME:PASSWORD@SERVER.postgres.database.azure.com:5432/DATABASE?sslmode=require
```

**Nếu password có ký tự đặc biệt, encode:**
- `!` → `%21`
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`

### SSH vào Container (Debug)

1. Menu trái → **"SSH"**
2. Click **"Go →"**
3. Chạy lệnh debug:

```bash
cd /home/site/wwwroot
ls -la
python manage.py check
python manage.py showmigrations
env | grep DJANGO
```

---

## 📊 Chi Phí Dự Kiến

| Service | Tier | Giá/tháng |
|---------|------|-----------|
| PostgreSQL | Burstable B1ms | ~$12 |
| App Service | Free F1 | $0 (giới hạn) |
| App Service | Basic B1 | ~$13 |
| **Tổng (Production)** | | **~$25/tháng** |

---

## ✅ Checklist Hoàn Chỉnh

- [ ] PostgreSQL server created
- [ ] Database "myhealthcare" created  
- [ ] Firewall rules configured
- [ ] Web App created với Python 3.11
- [ ] 5 Environment variables set
- [ ] Startup command configured
- [ ] Code deployed (GitHub/Git)
- [ ] Logs checked (no errors)
- [ ] App restarted
- [ ] URL works: `https://your-app.azurewebsites.net/api/v1/admin/`
- [ ] Test API register successfully

---

## 🔗 Links Hữu Ích

- [Azure Portal](https://portal.azure.com)
- [Azure App Service Docs](https://docs.microsoft.com/azure/app-service/)
- [Django on Azure Guide](https://docs.microsoft.com/azure/app-service/configure-language-python)

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Check **Log stream** trước
2. Verify tất cả **Environment variables**
3. Test **Database connection**
4. SSH vào container để debug

**Chúc bạn deploy thành công! 🎉**

