# 📦 Hướng dẫn Deployment - MyHealthCare API

Repo này có 3 workflows để deploy lên Azure:

## 🎯 Chọn phương án phù hợp

| Phương án | Độ khó | Thời gian | Tự động? | Phù hợp cho |
|-----------|--------|-----------|----------|-------------|
| **1. Azure CLI Direct** | ⭐ Dễ | 5 phút | ❌ Không | Testing nhanh |
| **2. GitHub Actions (Simple)** | ⭐⭐ Trung bình | 10 phút | ✅ Có | Development |
| **3. GitHub Actions (Full)** | ⭐⭐⭐ Nâng cao | 15 phút | ✅ Có | Production |

---

## 🚀 Phương án 1: Azure CLI Direct (Nhanh nhất)

**File cần có:**
- ✅ `.deployment` (root)
- ✅ `backend/startup.sh`
- ✅ `backend/runtime.txt`

**Các bước:**

```bash
# 1. Login
az login

# 2. Deploy (1 lệnh)
az webapp up --runtime PYTHON:3.11 --sku B1 \
  --location "Southeast Asia" \
  --resource-group myhealthcare-rg \
  --name your-app-name

# 3. Config startup
az webapp config set --resource-group myhealthcare-rg \
  --name your-app-name --startup-file "backend/startup.sh"

# 4. Set env vars
az webapp config appsettings set \
  --resource-group myhealthcare-rg --name your-app-name \
  --settings DJANGO_SECRET_KEY="xxx" DJANGO_DEBUG=False
```

**Ưu điểm:** Nhanh, đơn giản  
**Nhược điểm:** Phải deploy thủ công mỗi lần

📖 Chi tiết: [`/QUICKSTART_AZURE.md`](../../QUICKSTART_AZURE.md)

---

## ⚙️ Phương án 2: GitHub Actions (Simple)

**File workflow:** `.github/workflows/simple-deploy.yml`

**Đặc điểm:**
- ✅ Tự động deploy khi push code
- ✅ Chỉ deploy khi có thay đổi trong `backend/`
- ⚠️ Không run tests
- ⚠️ Không check code quality

**Setup:**

1. **Get Azure credentials:**
```bash
az webapp deployment list-publishing-profiles \
  --resource-group myhealthcare-rg \
  --name your-app-name --xml
```

2. **Add GitHub Secrets:**
   - `AZURE_WEBAPP_NAME`: tên app
   - `AZURE_WEBAPP_PUBLISH_PROFILE`: XML từ bước 1

3. **Push code:**
```bash
git push origin main
```

**Khi nào dùng:** Development, testing, personal projects

---

## 🏆 Phương án 3: GitHub Actions (Full CI/CD)

**File workflow:** `.github/workflows/azure-deploy.yml`

**Đặc điểm:**
- ✅ Tự động deploy
- ✅ Run tests trước khi deploy
- ✅ Setup Python environment
- ✅ Install dependencies
- ✅ Coverage report
- ✅ Set startup command

**Pipeline:**
```
📝 Checkout → 🐍 Setup Python → 📦 Install deps 
   ↓
🧪 Run tests → ✅ Pass? → 🚀 Deploy to Azure → ⚙️ Configure
   ↓
❌ Fail? → Stop (không deploy)
```

**Setup:**

1. **GitHub Secrets** (3 secrets):
   - `AZURE_WEBAPP_NAME`
   - `AZURE_WEBAPP_PUBLISH_PROFILE`
   - `AZURE_RESOURCE_GROUP`

2. **Azure Environment Variables:**
```bash
az webapp config appsettings set --name your-app \
  --settings \
    DJANGO_SECRET_KEY="xxx" \
    DJANGO_DEBUG=False \
    DJANGO_ALLOWED_HOSTS="your-app.azurewebsites.net" \
    DATABASE_URL="postgresql://..."
```

3. **Push code:**
```bash
git push origin main
```

**Khi nào dùng:** Production, team projects, CI/CD requirements

📖 Chi tiết: [`.github/workflows/README.md`](./workflows/README.md)

---

## 📁 Cấu trúc Files

```
MyHealthCare/
├── .deployment                          # ← Azure project config
├── .github/
│   └── workflows/
│       ├── simple-deploy.yml           # ← Simple workflow
│       ├── azure-deploy.yml            # ← Full CI/CD workflow
│       └── README.md                   # ← Workflow docs
├── backend/
│   ├── startup.sh                      # ← Azure startup script
│   ├── runtime.txt                     # ← Python version
│   ├── requirements.txt                # ← Dependencies
│   └── ...
├── QUICKSTART_AZURE.md                 # ← Quick guide
└── AZURE_DEPLOYMENT.md                 # ← Detailed guide
```

---

## 🔧 Environment Variables cần thiết

### Development
```bash
DJANGO_SECRET_KEY=dev-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Production (Azure)
```bash
DJANGO_SECRET_KEY=<generate-random-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app.azurewebsites.net
DATABASE_URL=postgresql://user:pass@host:5432/db
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🗄️ Database Options

### Option 1: Azure PostgreSQL
```bash
az postgres flexible-server create \
  --name myhealthcare-db \
  --resource-group myhealthcare-rg \
  --admin-user myadmin \
  --admin-password <password>
```

**Cost:** ~$25/month (Burstable B1ms)

### Option 2: ElephantSQL (Free)
1. Go to [elephantsql.com](https://www.elephantsql.com/)
2. Create free instance (20MB)
3. Copy connection URL
4. Set `DATABASE_URL` in Azure

**Cost:** Free (limited 20MB)

### Option 3: Supabase
1. Create project at [supabase.com](https://supabase.com/)
2. Get PostgreSQL connection string
3. Set `DATABASE_URL`

**Cost:** Free (500MB)

---

## 📊 Monitoring & Debugging

### View logs
```bash
# Real-time
az webapp log tail -g myhealthcare-rg -n your-app

# Download
az webapp log download -g myhealthcare-rg -n your-app
```

### SSH into container
```bash
az webapp ssh -g myhealthcare-rg -n your-app
```

### Restart app
```bash
az webapp restart -g myhealthcare-rg -n your-app
```

### Check health
```bash
curl https://your-app.azurewebsites.net/api/v1/admin/
```

---

## ✅ Pre-deployment Checklist

- [ ] File `.deployment` ở root folder
- [ ] File `backend/startup.sh` có quyền execute
- [ ] File `backend/runtime.txt` có Python version
- [ ] File `requirements.txt` đầy đủ dependencies
- [ ] Environment variables được set trên Azure
- [ ] Database connection string đúng
- [ ] `ALLOWED_HOSTS` bao gồm Azure domain
- [ ] `DEBUG=False` trong production
- [ ] `SECRET_KEY` được generate random
- [ ] Tests pass locally: `pytest --cov`
- [ ] GitHub secrets được add (nếu dùng Actions)

---

## 🆘 Troubleshooting

### App không start
- Check logs: `az webapp log tail`
- Verify startup command: `az webapp config show`
- Check environment variables

### Database connection error
- Verify `DATABASE_URL` format
- Check firewall rules (allow Azure services)
- Test connection locally

### Static files missing
- Check `STATIC_ROOT` trong settings
- Run `python manage.py collectstatic`
- Verify WhiteNoise configuration

### Tests fail in GitHub Actions
- Check Python version matches
- Verify all dependencies in requirements.txt
- Check test database configuration

---

## 📚 Tài liệu tham khảo

- 📖 [QUICKSTART_AZURE.md](../../QUICKSTART_AZURE.md) - Quick start guide
- 📖 [AZURE_DEPLOYMENT.md](../../AZURE_DEPLOYMENT.md) - Detailed guide
- 📖 [workflows/README.md](./workflows/README.md) - GitHub Actions guide
- 🔗 [Azure App Service Docs](https://docs.microsoft.com/azure/app-service/)
- 🔗 [Django on Azure](https://docs.microsoft.com/azure/app-service/configure-language-python)

---

## 💡 Tips

1. **Start với Simple workflow** cho development, chuyển sang Full CI/CD khi cần
2. **Dùng Free tier** (F1) cho testing, B1 cho production
3. **Monitor logs** sau mỗi lần deploy
4. **Setup database** trước khi deploy
5. **Test locally** trước: `pytest --cov`
6. **Backup database** trước khi migrate

---

**Happy Deploying! 🚀**

