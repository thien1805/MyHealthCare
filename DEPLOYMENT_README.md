# 🚀 Deployment Files - Tổng quan

Tôi đã tạo đầy đủ các files và workflows để deploy Django app từ folder `backend` lên Azure App Service.

## 📁 Files đã được tạo

### 1. Configuration Files

```
✅ .deployment                           # Chỉ cho Azure biết code ở folder backend
✅ backend/startup.sh                    # Script chạy khi start app
✅ backend/runtime.txt                   # Python version (3.11.9)
✅ backend/.gitignore                    # Ignore files cho backend
```

### 2. GitHub Actions Workflows

```
✅ .github/workflows/simple-deploy.yml   # Workflow đơn giản (chỉ deploy)
✅ .github/workflows/azure-deploy.yml    # Workflow đầy đủ (test + deploy)
✅ .github/workflows/README.md           # Hướng dẫn setup workflows
```

### 3. Deployment Scripts

```
✅ deploy.sh                             # Script tự động deploy từ local
✅ .azure/deploy.sh                      # Azure deployment script
```

### 4. Documentation

```
✅ QUICKSTART_AZURE.md                   # Hướng dẫn nhanh (5 phút)
✅ AZURE_DEPLOYMENT.md                   # Hướng dẫn chi tiết đầy đủ
✅ .github/DEPLOYMENT_GUIDE.md           # So sánh các phương án deploy
```

---

## 🎯 3 Cách Deploy

### Cách 1: Script tự động (⚡ Dễ nhất - 1 lệnh)

```bash
# Cho phép script chạy
chmod +x deploy.sh

# Deploy
./deploy.sh [resource-group] [app-name]

# Ví dụ:
./deploy.sh myhealthcare-rg my-health-api
```

**Ưu điểm:** Tự động mọi thứ, dễ dàng nhất  
**Nhược điểm:** Cần Azure CLI

---

### Cách 2: GitHub Actions - Simple (🔄 Tự động, không test)

**File:** `.github/workflows/simple-deploy.yml`

**Setup:**
1. Lấy publish profile từ Azure
2. Add vào GitHub Secrets:
   - `AZURE_WEBAPP_NAME`
   - `AZURE_WEBAPP_PUBLISH_PROFILE`
3. Push code → Tự động deploy

**Khi nào deploy:** Khi có thay đổi trong `backend/` folder

---

### Cách 3: GitHub Actions - Full CI/CD (✅ Tự động + Test)

**File:** `.github/workflows/azure-deploy.yml`

**Setup:**
1. Add 3 GitHub Secrets:
   - `AZURE_WEBAPP_NAME`
   - `AZURE_WEBAPP_PUBLISH_PROFILE`
   - `AZURE_RESOURCE_GROUP`
2. Push code → Chạy test → Deploy (nếu test pass)

**Pipeline:**
```
Checkout → Setup Python → Install deps → Run tests
   ↓
Pass? → Deploy → Configure
   ↓
Fail? → STOP (không deploy)
```

---

## ⚡ Quick Start (Chọn 1 cách)

### Option A: Dùng Script (Nhanh nhất)

```bash
# 1. Make script executable
chmod +x deploy.sh

# 2. Run
./deploy.sh

# 3. Set database URL
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api \
  --settings DATABASE_URL="postgresql://..."
```

### Option B: Dùng GitHub Actions

```bash
# 1. Tạo Azure app
az webapp up --runtime PYTHON:3.11 --sku B1 \
  --location "Southeast Asia" \
  --resource-group myhealthcare-rg \
  --name your-app-name

# 2. Get publish profile
az webapp deployment list-publishing-profiles \
  --resource-group myhealthcare-rg \
  --name your-app-name --xml

# 3. Add to GitHub Secrets (Settings → Secrets → Actions)
#    - AZURE_WEBAPP_NAME: your-app-name
#    - AZURE_WEBAPP_PUBLISH_PROFILE: (XML từ step 2)
#    - AZURE_RESOURCE_GROUP: myhealthcare-rg

# 4. Push code
git add .
git commit -m "Setup deployment"
git push origin main
```

---

## 🔧 Environment Variables cần set trên Azure

```bash
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name your-app-name \
  --settings \
    DJANGO_SECRET_KEY="$(openssl rand -base64 32)" \
    DJANGO_DEBUG=False \
    DJANGO_ALLOWED_HOSTS="your-app-name.azurewebsites.net" \
    DATABASE_URL="postgresql://user:pass@host:5432/db"
```

Hoặc set từ Azure Portal:
- App Service → Configuration → Application settings

---

## 📖 Chi tiết hơn?

| File | Mô tả |
|------|-------|
| [`QUICKSTART_AZURE.md`](./QUICKSTART_AZURE.md) | Hướng dẫn nhanh, step-by-step |
| [`AZURE_DEPLOYMENT.md`](./AZURE_DEPLOYMENT.md) | Hướng dẫn đầy đủ, tất cả options |
| [`.github/DEPLOYMENT_GUIDE.md`](./.github/DEPLOYMENT_GUIDE.md) | So sánh workflows |
| [`.github/workflows/README.md`](./.github/workflows/README.md) | Setup GitHub Actions |

---

## ✅ Checklist trước khi deploy

- [ ] File `.deployment` có ở root folder
- [ ] File `backend/startup.sh` hoàn chỉnh
- [ ] File `backend/runtime.txt` có Python version
- [ ] Tests pass: `cd backend && pytest --cov`
- [ ] Database đã setup (Azure PostgreSQL/ElephantSQL/Supabase)
- [ ] Environment variables ready

---

## 🗄️ Setup Database

### Free Options:

**ElephantSQL** (Free 20MB)
1. Tạo tài khoản: https://www.elephantsql.com/
2. Tạo instance (Tiny Turtle - Free)
3. Copy URL
4. Set `DATABASE_URL` trên Azure

**Supabase** (Free 500MB)
1. Tạo project: https://supabase.com/
2. Vào Settings → Database
3. Copy Connection String (URI format)
4. Set `DATABASE_URL`

### Paid Option:

**Azure PostgreSQL** (~$25/month)
```bash
az postgres flexible-server create \
  --name myhealthcare-db \
  --resource-group myhealthcare-rg \
  --admin-user myadmin \
  --admin-password YourPassword123!
```

---

## 🔍 Debug & Monitor

```bash
# Xem logs real-time
az webapp log tail -g myhealthcare-rg -n your-app-name

# SSH vào container
az webapp ssh -g myhealthcare-rg -n your-app-name

# Restart app
az webapp restart -g myhealthcare-rg -n your-app-name

# Check status
curl https://your-app-name.azurewebsites.net/api/v1/admin/
```

---

## 💰 Chi phí

| Tier | Giá | Dùng cho |
|------|-----|----------|
| F1 (Free) | $0/tháng | Testing |
| B1 (Basic) | ~$13/tháng | Development |
| S1 (Standard) | ~$70/tháng | Production |

---

## 🆘 Cần help?

1. **Deployment script không chạy?**
   ```bash
   chmod +x deploy.sh
   ```

2. **GitHub Actions fail?**
   - Check secrets đã add chưa
   - Xem logs trong Actions tab

3. **App không start?**
   ```bash
   az webapp log tail -g myhealthcare-rg -n your-app
   ```

4. **Database connection error?**
   - Verify `DATABASE_URL` format
   - Check firewall rules

---

## 📚 Resources

- 🔗 [Azure App Service Docs](https://docs.microsoft.com/azure/app-service/)
- 🔗 [Django on Azure](https://docs.microsoft.com/azure/app-service/configure-language-python)
- 🔗 [GitHub Actions for Azure](https://github.com/Azure/actions)

---

**🎉 Happy Deploying!**

Nếu gặp vấn đề, check các file hướng dẫn chi tiết ở trên hoặc xem logs!

