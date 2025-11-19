# GitHub Actions Workflows

## Azure Deployment

Workflow này sẽ tự động deploy ứng dụng Django lên Azure App Service khi có push vào branch `main` hoặc `master`.

### Cấu hình cần thiết

Bạn cần thêm các secrets sau vào GitHub repository:

1. **AZURE_WEBAPP_NAME**: Tên của Azure App Service
   - Ví dụ: `myhealthcare-app`

2. **AZURE_WEBAPP_PUBLISH_PROFILE**: Publish profile từ Azure
   - Lấy từ Azure Portal: App Service → Get publish profile
   - Copy toàn bộ nội dung XML file

3. **AZURE_RESOURCE_GROUP**: Tên Resource Group trên Azure
   - Ví dụ: `myhealthcare-rg`

### Cách thêm secrets:

1. Vào GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Thêm từng secret với tên và giá trị tương ứng

### Workflow sẽ làm gì:

1. ✅ Checkout code
2. ✅ Setup Python 3.11
3. ✅ Install dependencies từ `backend/requirements.txt`
4. ✅ Run tests với pytest
5. ✅ Deploy lên Azure App Service
6. ✅ Set startup command cho Azure

### Azure App Service Configuration

File `.deployment` ở root folder sẽ chỉ định cho Azure biết code chính nằm trong folder `backend`.

### Startup Command

Azure sẽ chạy file `backend/startup.sh` để:
- Migrate database
- Collect static files
- Start Gunicorn server

### Environment Variables trên Azure

Đừng quên set các environment variables trên Azure Portal:

```bash
ALLOWED_HOSTS=your-app.azurewebsites.net
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Manual Deployment

Nếu muốn deploy thủ công, vào Actions tab và click "Run workflow".

