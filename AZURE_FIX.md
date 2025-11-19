# 🔧 FIX AZURE DEPLOYMENT - Backend Folder Issue

## ✅ Đã Fix Các Files Sau:

1. **`backend/startup.sh`** - Đơn giản hóa, bỏ install thừa
2. **`.deployment`** - Cấu hình chính xác cho folder backend
3. **`oryx-manifest.toml`** - Giúp Azure Oryx hiểu cấu trúc
4. **`.azure.yml`** - Azure config file
5. **`backend/.deployment`** - Local deployment config

---

## 🚀 HƯỚNG DẪN DEPLOY LẠI

### Bước 1: Commit và Push Changes

```bash
cd /Users/thien2005/Workspace/PROJECT/MyHealthCare

# Check changes
git status

# Add all changes
git add .

# Commit
git commit -m "Fix Azure deployment - optimize startup.sh and add build configs"

# Push to GitHub
git push origin main
```

### Bước 2: Trên Azure Portal

#### 2.1. Xóa Configuration Cũ (Nếu Có Lỗi)

1. Vào **Web App** của bạn
2. **Configuration** → **General settings**
3. **Startup Command**: Xóa trống hoặc set lại: `backend/startup.sh`
4. Click **Save**

#### 2.2. Verify Environment Variables

**Configuration** → **Application settings** - Đảm bảo có đủ:

```
DJANGO_SECRET_KEY = <your-secret-key>
DJANGO_DEBUG = False
DJANGO_ALLOWED_HOSTS = <your-app-name>.azurewebsites.net
AZURE_POSTGRESQL_CONNECTIONSTRING = postgresql://...
SCM_DO_BUILD_DURING_DEPLOYMENT = true
WEBSITE_HOSTNAME = <your-app-name>.azurewebsites.net
```

#### 2.3. Redeploy

**Option A: Từ GitHub (Tự động)**

1. **Deployment Center** → Chọn **GitHub**
2. Select repository và branch
3. Click **Save** → Azure sẽ tự động deploy

**Option B: Manual Sync**

1. **Deployment Center** → Tab **Logs**
2. Click **Sync** button
3. Đợi 5-10 phút

#### 2.4. Restart App

1. Trang **Overview**
2. Click **Restart**
3. Đợi 1 phút

---

## 🔍 KIỂM TRA DEPLOYMENT

### 1. Xem Build Logs

```
Deployment Center → Logs → Click vào deployment mới nhất
```

Tìm các dòng quan trọng:
```
✓ Detected platform: Python 3.11
✓ Building in source directory: /tmp/8d.../backend
✓ Running pip install -r requirements.txt
✓ Build succeeded
```

### 2. Xem Application Logs

```
Log stream (menu bên trái)
```

Tìm:
```
Starting Django application...
Running database migrations...
Collecting static files...
Starting Gunicorn server...
```

### 3. Test Endpoints

```bash
# Health check
curl https://<your-app>.azurewebsites.net/api/v1/admin/

# Should return Django admin page HTML
```

---

## ❌ NẾU VẪN GẶP LỖI

### Lỗi: "Application Error" hoặc 500

**SSH vào container:**

```bash
# Trong Azure Portal: SSH → Go
cd /home/site/wwwroot

# Check structure
ls -la
# Should see: backend/ folder and .deployment file

cd backend
ls -la
# Should see: manage.py, startup.sh, requirements.txt

# Test Django
python manage.py check

# Test Gunicorn
gunicorn --bind=0.0.0.0:8000 myhealthcare.wsgi:application
```

### Lỗi: Build Failed

**Check build logs:**
- Xem có lỗi install packages không
- Verify requirements.txt đúng format
- Check Python version compatible

**Fix:**
```bash
# Local test trước
cd backend
pip install -r requirements.txt
python manage.py check
```

### Lỗi: Can't find startup.sh

**Verify file permissions:**
```bash
# Local machine
cd backend
chmod +x startup.sh
git add startup.sh
git commit -m "Make startup.sh executable"
git push
```

---

## 📋 STARTUP COMMAND OPTIONS

Trên Azure Portal → Configuration → General settings → Startup Command

**Option 1: Dùng startup.sh (Khuyên dùng)**
```
backend/startup.sh
```

**Option 2: Trực tiếp Gunicorn**
```
gunicorn --chdir backend --bind=0.0.0.0:8000 --timeout=600 myhealthcare.wsgi:application
```

**Option 3: Python module**
```
python -m gunicorn --chdir backend --bind=0.0.0.0:8000 myhealthcare.wsgi:application
```

---

## 🎯 CHECKLIST ĐÚNG

- [ ] ✅ File `.deployment` ở ROOT folder
- [ ] ✅ File `backend/startup.sh` có quyền execute (chmod +x)
- [ ] ✅ File `backend/requirements.txt` đầy đủ
- [ ] ✅ File `backend/runtime.txt` có Python 3.11.9
- [ ] ✅ Environment variables đủ 6 cái trên Azure
- [ ] ✅ Startup command = `backend/startup.sh`
- [ ] ✅ Database PostgreSQL đã tạo và allow Azure
- [ ] ✅ Code đã push lên GitHub/Azure Git
- [ ] ✅ Deployment logs showing success
- [ ] ✅ Application logs không có ERROR
- [ ] ✅ URL works: https://your-app.azurewebsites.net

---

## 💡 TIPS

1. **Luôn check logs trước**: Log stream là bạn thân nhất
2. **Test local trước**: `python manage.py check` và `gunicorn` local
3. **Deploy từng bước**: Fix 1 lỗi, test, rồi tiếp
4. **Restart sau mỗi config change**: Azure cần restart để apply settings
5. **Dùng SSH để debug**: Vào container xem trực tiếp

---

## 🆘 VẪN KHÔNG WORK?

### Debug Chi Tiết:

1. **Get exact error message** từ logs
2. **Screenshot** deployment logs và application logs
3. **Run in SSH:**
```bash
cd /home/site/wwwroot/backend
python manage.py check --deploy
python manage.py showmigrations
python manage.py collectstatic --dry-run
env | grep DJANGO
```

4. **Test database connection:**
```bash
python manage.py dbshell
# Type: \q to exit if successful
```

---

## ✅ SUCCESS OUTPUT

Khi deploy thành công, bạn sẽ thấy trong logs:

```
Starting Django application...
Running database migrations...
Operations to perform:
  Apply all migrations: accounts, admin, auth, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  ...
Collecting static files...
X static files copied to '/home/site/wwwroot/backend/staticfiles'.
Starting Gunicorn server...
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXX
```

Và URL sẽ work: `https://your-app.azurewebsites.net/api/v1/admin/` 🎉

---

**Làm theo guide này từng bước và cho tôi biết ở bước nào bạn gặp lỗi!** 📝

