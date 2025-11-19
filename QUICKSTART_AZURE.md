# 🚀 Hướng dẫn Deploy lên Azure - Nhanh gọn

## ⚡ Cách nhanh nhất (5 phút)

### Bước 1: Tạo Azure Web App

```bash
# Login vào Azure
az login

# Tạo mọi thứ trong 1 lệnh
az webapp up \
  --runtime PYTHON:3.11 \
  --sku B1 \
  --location "Southeast Asia" \
  --resource-group myhealthcare-rg \
  --name <tên-app-của-bạn>
```

### Bước 2: Set Environment Variables

```bash
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name <tên-app-của-bạn> \
  --settings \
    DJANGO_SECRET_KEY="$(openssl rand -base64 32)" \
    DJANGO_DEBUG=False \
    DJANGO_ALLOWED_HOSTS="<tên-app-của-bạn>.azurewebsites.net" \
    DATABASE_URL="<your-database-url>"
```

### Bước 3: Set Startup Command

```bash
az webapp config set \
  --resource-group myhealthcare-rg \
  --name <tên-app-của-bạn> \
  --startup-file "backend/startup.sh"
```

### Bước 4: Deploy

Push code lên Git:

```bash
git add .
git commit -m "Azure deployment setup"
git push
```

**XONG!** 🎉 App của bạn sẽ có tại: `https://<tên-app-của-bạn>.azurewebsites.net`

---

## 🔧 Setup GitHub Actions (Tự động deploy)

### 1. Lấy Publish Profile từ Azure

```bash
# Download publish profile
az webapp deployment list-publishing-profiles \
  --resource-group myhealthcare-rg \
  --name <tên-app-của-bạn> \
  --xml
```

Copy output (XML content)

### 2. Thêm vào GitHub Secrets

Vào GitHub repo → **Settings** → **Secrets and variables** → **Actions**

Tạo 3 secrets:

| Tên | Giá trị |
|-----|---------|
| `AZURE_WEBAPP_NAME` | `<tên-app-của-bạn>` |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | (XML content từ bước 1) |
| `AZURE_RESOURCE_GROUP` | `myhealthcare-rg` |

### 3. Push và xem magic ✨

```bash
git push origin main
```

Vào **Actions** tab để xem deployment progress!

---

## 📝 Environment Variables cần thiết

Vào Azure Portal → App Service → **Configuration** → **Application settings**

Hoặc dùng CLI:

```bash
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name <tên-app> \
  --settings \
    DJANGO_SECRET_KEY="your-secret-key" \
    DJANGO_DEBUG="False" \
    DJANGO_ALLOWED_HOSTS="<tên-app>.azurewebsites.net" \
    DATABASE_URL="postgresql://user:pass@host:5432/db"
```

### Generate SECRET_KEY

```bash
# Linux/Mac
openssl rand -base64 32

# Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🗄️ Setup Database (PostgreSQL)

### Option 1: Azure Database for PostgreSQL

```bash
# Tạo server
az postgres flexible-server create \
  --name myhealthcare-db \
  --resource-group myhealthcare-rg \
  --location "Southeast Asia" \
  --admin-user myadmin \
  --admin-password <password> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14

# Allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group myhealthcare-rg \
  --name myhealthcare-db \
  --rule-name AllowAzure \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Connection string
DATABASE_URL=postgresql://myadmin:<password>@myhealthcare-db.postgres.database.azure.com:5432/postgres?sslmode=require
```

### Option 2: ElephantSQL (Free tier)

1. Vào [elephantsql.com](https://www.elephantsql.com/)
2. Tạo free instance
3. Copy connection URL
4. Set vào Azure:

```bash
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name <tên-app> \
  --settings DATABASE_URL="<elephantsql-url>"
```

---

## 🔍 Troubleshooting

### Xem logs

```bash
# Xem logs realtime
az webapp log tail --resource-group myhealthcare-rg --name <tên-app>

# Download logs
az webapp log download --resource-group myhealthcare-rg --name <tên-app>
```

### SSH vào container

```bash
az webapp ssh --resource-group myhealthcare-rg --name <tên-app>
```

### Restart app

```bash
az webapp restart --resource-group myhealthcare-rg --name <tên-app>
```

### Check configuration

```bash
az webapp config show --resource-group myhealthcare-rg --name <tên-app>
```

---

## 💰 Pricing

| Tier | Giá/tháng | RAM | CPU | Dùng cho |
|------|-----------|-----|-----|----------|
| F1 (Free) | $0 | 1GB | Shared | Testing |
| B1 (Basic) | ~$13 | 1.75GB | 1 Core | Dev/Small apps |
| S1 (Standard) | ~$70 | 1.75GB | 1 Core | Production |
| P1V2 (Premium) | ~$85 | 3.5GB | 1 Core | High traffic |

### Dùng Free tier:

```bash
az appservice plan create \
  --name myhealthcare-plan \
  --resource-group myhealthcare-rg \
  --sku F1 \
  --is-linux
```

---

## 📚 Files quan trọng

### ✅ `.deployment` (Root folder)
```
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
project = backend
```
→ Chỉ cho Azure biết code ở folder `backend`

### ✅ `backend/startup.sh`
```bash
#!/bin/bash
python manage.py migrate --no-input
python manage.py collectstatic --no-input
gunicorn --bind=0.0.0.0 --timeout 600 myhealthcare.wsgi:application
```
→ Script chạy khi start app

### ✅ `backend/runtime.txt`
```
python-3.11.9
```
→ Specify Python version

### ✅ `.github/workflows/simple-deploy.yml`
→ GitHub Actions workflow (tự động deploy)

---

## ✅ Checklist

- [ ] Tạo Azure Web App
- [ ] Set environment variables (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL)
- [ ] Set startup command
- [ ] Setup database (PostgreSQL)
- [ ] Add GitHub secrets (nếu dùng GitHub Actions)
- [ ] Push code
- [ ] Check logs
- [ ] Test API endpoints

---

## 🎯 Test sau khi deploy

```bash
# Health check
curl https://<tên-app>.azurewebsites.net/api/v1/admin/

# Test register
curl -X POST https://<tên-app>.azurewebsites.net/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "full_name": "Test User",
    "phone_num": "0901234567",
    "role": "patient"
  }'
```

---

**Cần help?** Check file `AZURE_DEPLOYMENT.md` để xem chi tiết hơn! 📖

