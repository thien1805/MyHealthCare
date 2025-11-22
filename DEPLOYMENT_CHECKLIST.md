# 📋 Deployment Checklist - Tránh Xung Đột Settings

## ⚠️ QUAN TRỌNG: Trước Khi Deploy

Sau khi chỉnh sửa `settings.py`, cần làm các bước sau để tránh xung đột:

---

## ✅ Checklist Trước Khi Deploy

### 1. Kiểm Tra Local Development
- [ ] Code chạy OK ở local với local database
- [ ] Test các API endpoints hoạt động bình thường
- [ ] Không có lỗi khi chạy `python manage.py check`
- [ ] Migrations đã được tạo và test: `python manage.py makemigrations` và `python manage.py migrate`

### 2. Kiểm Tra Environment Variables trên Azure

**Vào Azure Portal → Web App → Configuration → Application settings**

Đảm bảo có các biến sau:

| Biến | Giá trị | Bắt buộc |
|------|---------|----------|
| `DJANGO_SECRET_KEY` | (secret key) | ✅ |
| `DJANGO_DEBUG` | `False` | ✅ |
| `DJANGO_ALLOWED_HOSTS` | `<your-app-name>.azurewebsites.net` | ✅ |
| `AZURE_POSTGRESQL_CONNECTIONSTRING` | `postgresql://...` | ✅ |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | ✅ |

**LƯU Ý:** 
- `WEBSITE_HOSTNAME` được Azure tự động set, không cần thêm thủ công
- Nếu có `DATABASE_URL` cũ, có thể xóa (không cần thiết nếu đã có `AZURE_POSTGRESQL_CONNECTIONSTRING`)

### 3. Verify Database Connection String Format

Connection string phải có format:
```
postgresql://USERNAME:PASSWORD@SERVER.postgres.database.azure.com:5432/DATABASE?sslmode=require
```

**Kiểm tra:**
- [ ] Connection string có chứa `database.azure.com` (không phải localhost)
- [ ] Password đã được encode nếu có ký tự đặc biệt (`!` → `%21`, `@` → `%40`, etc.)
- [ ] Database name đúng (thường là `myhealthcare`)

### 4. Test Database Connection (Optional nhưng khuyên dùng)

**SSH vào Azure Web App:**
1. Azure Portal → Web App → SSH
2. Chạy lệnh:
```bash
cd /home/site/wwwroot
python manage.py check --database default
python manage.py showmigrations
```

Nếu không có lỗi → Database connection OK ✅

---

## 🚀 Quy Trình Deploy An Toàn

### Bước 1: Commit và Push Code
```bash
git add myhealthcare/settings.py
git commit -m "Update database configuration with production detection"
git push origin main  # hoặc branch của bạn
```

### Bước 2: Monitor Deployment

**GitHub Actions (nếu dùng):**
- Vào GitHub → Tab "Actions"
- Xem workflow đang chạy
- Đợi đến khi có ✅ xanh

**Hoặc Azure Deployment Center:**
- Vào Azure Portal → Web App → Deployment Center
- Xem deployment logs

### Bước 3: Verify Sau Khi Deploy

1. **Check Logs:**
   - Azure Portal → Web App → Log stream
   - Tìm các dòng:
     ```
     ✅ Operations to perform...
     ✅ Running migrations...
     ✅ Starting gunicorn...
     ```

2. **Test API:**
   - Mở browser: `https://<your-app>.azurewebsites.net/api/v1/admin/`
   - Phải thấy Django admin login page
   - Test một API endpoint: `https://<your-app>.azurewebsites.net/api/v1/auth/register/`

3. **Check Database:**
   - Nếu có lỗi database, xem Log stream để tìm lỗi cụ thể

---

## 🔍 Logic Detection Database (Hiểu Rõ)

### Production Detection:
```python
IS_PRODUCTION = (
    WEBSITE_HOSTNAME exists  # Azure tự động set
    OR
    (Connection string có 'database.azure.com' AND DEBUG=False)
)
```

### Kết Quả:
- **Production** → Dùng `AZURE_POSTGRESQL_CONNECTIONSTRING` hoặc `DATABASE_URL`
- **Development** → Dùng local database (pgservice hoặc DB_NAME/DB_USER/...)

---

## ⚠️ Các Trường Hợp Có Thể Xảy Ra

### Trường Hợp 1: Deploy lần đầu
✅ **Không có vấn đề** - Logic mới sẽ tự động detect production

### Trường Hợp 2: Đã có deployment cũ
✅ **Backward compatible** - Nếu có `AZURE_POSTGRESQL_CONNECTIONSTRING` với `database.azure.com`, sẽ tự động dùng production database

### Trường Hợp 3: Local có connection string trong .env
✅ **An toàn** - Logic sẽ check `localhost` trong connection string, nếu có thì vẫn dùng local database

---

## 🐛 Troubleshooting

### Lỗi: "Production environment detected but no database connection string found"

**Nguyên nhân:** 
- `WEBSITE_HOSTNAME` tồn tại (Azure set) nhưng không có `AZURE_POSTGRESQL_CONNECTIONSTRING` hoặc `DATABASE_URL`

**Cách fix:**
1. Vào Azure Portal → Configuration → Application settings
2. Thêm `AZURE_POSTGRESQL_CONNECTIONSTRING` với connection string đúng
3. Save → Restart app

### Lỗi: "Database connection failed"

**Nguyên nhân:**
- Connection string sai format
- Password chưa encode ký tự đặc biệt
- Firewall chưa allow Azure services

**Cách fix:**
1. Verify connection string format
2. Encode password nếu cần
3. Azure Portal → PostgreSQL → Networking → Allow Azure services

### Lỗi: Local vẫn kết nối Azure database

**Nguyên nhân:**
- Có `WEBSITE_HOSTNAME` trong `.env` local (không nên có)

**Cách fix:**
1. Xóa `WEBSITE_HOSTNAME` khỏi `.env` local
2. Đảm bảo `.env` chỉ có local database config

---

## ✅ Final Checklist

Sau khi deploy xong, verify:

- [ ] App start thành công (check Log stream)
- [ ] API endpoints hoạt động
- [ ] Database connection OK (không có lỗi trong logs)
- [ ] Local development vẫn dùng local database
- [ ] Production dùng Azure database

---

## 📝 Notes

- **KHÔNG BAO GIỜ** commit file `.env` lên Git
- **KHÔNG BAO GIỜ** set `WEBSITE_HOSTNAME` trong `.env` local
- Azure tự động set `WEBSITE_HOSTNAME` khi deploy, không cần set thủ công
- Logic mới **backward compatible** với settings cũ

---

**Chúc bạn deploy thành công! 🎉**

