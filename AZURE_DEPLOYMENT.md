# Hướng dẫn Deploy lên Azure App Service

## Phương án 1: Deploy tự động với GitHub Actions (Khuyên dùng)

### Bước 1: Cấu hình Azure App Service

1. Tạo Azure App Service:
```bash
az webapp create \
  --resource-group <resource-group-name> \
  --plan <app-service-plan> \
  --name <app-name> \
  --runtime "PYTHON:3.11"
```

2. Lấy Publish Profile:
   - Vào Azure Portal → App Service → Get publish profile
   - Download file XML

### Bước 2: Cấu hình GitHub Secrets

Vào GitHub repository → Settings → Secrets and variables → Actions

Thêm các secrets sau:

| Secret Name | Mô tả | Ví dụ |
|------------|-------|-------|
| `AZURE_WEBAPP_NAME` | Tên Azure App Service | `myhealthcare-api` |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Nội dung file publish profile | (XML content) |
| `AZURE_RESOURCE_GROUP` | Tên resource group | `myhealthcare-rg` |

### Bước 3: Cấu hình Environment Variables trên Azure

```bash
az webapp config appsettings set \
  --resource-group <resource-group> \
  --name <app-name> \
  --settings \
    DEBUG=False \
    SECRET_KEY="your-secret-key-here" \
    ALLOWED_HOSTS="<app-name>.azurewebsites.net" \
    DATABASE_URL="postgresql://user:password@host:5432/dbname"
```

Hoặc từ Azure Portal:
- App Service → Configuration → Application settings
- Thêm các biến:
  - `DEBUG`: `False`
  - `SECRET_KEY`: `<your-secret-key>`
  - `ALLOWED_HOSTS`: `<app-name>.azurewebsites.net`
  - `DATABASE_URL`: `postgresql://...`

### Bước 4: Deploy

Push code lên branch `main` hoặc `master`:

```bash
git add .
git commit -m "Setup Azure deployment"
git push origin main
```

GitHub Actions sẽ tự động:
1. ✅ Run tests
2. ✅ Build application
3. ✅ Deploy lên Azure
4. ✅ Run migrations
5. ✅ Collect static files

---

## Phương án 2: Deploy thủ công từ Azure

### Bước 1: Tạo Azure App Service

```bash
# Tạo resource group
az group create --name myhealthcare-rg --location "Southeast Asia"

# Tạo App Service plan
az appservice plan create \
  --name myhealthcare-plan \
  --resource-group myhealthcare-rg \
  --sku B1 \
  --is-linux

# Tạo Web App
az webapp create \
  --resource-group myhealthcare-rg \
  --plan myhealthcare-plan \
  --name myhealthcare-api \
  --runtime "PYTHON:3.11"
```

### Bước 2: Cấu hình Deployment từ Git

```bash
# Kết nối với GitHub repository
az webapp deployment source config \
  --name myhealthcare-api \
  --resource-group myhealthcare-rg \
  --repo-url https://github.com/<your-username>/<your-repo> \
  --branch main \
  --manual-integration
```

### Bước 3: Set Startup Command

```bash
az webapp config set \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api \
  --startup-file "backend/startup.sh"
```

### Bước 4: Cấu hình Environment Variables

```bash
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api \
  --settings \
    DEBUG=False \
    SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
    ALLOWED_HOSTS="myhealthcare-api.azurewebsites.net" \
    DATABASE_URL="postgresql://user:password@host:5432/myhealthcare"
```

### Bước 5: Deploy

```bash
# Sync deployment từ repo
az webapp deployment source sync \
  --name myhealthcare-api \
  --resource-group myhealthcare-rg
```

---

## Phương án 3: Deploy với Azure CLI (Local)

### Bước 1: Login Azure

```bash
az login
```

### Bước 2: Create và Deploy Web App

```bash
# Deploy trực tiếp từ local
az webapp up \
  --runtime PYTHON:3.11 \
  --sku B1 \
  --location "Southeast Asia" \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api
```

### Bước 3: Set Configuration

```bash
# Set startup command
az webapp config set \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api \
  --startup-file "backend/startup.sh"

# Set app settings
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api \
  --settings @appsettings.json
```

Tạo file `appsettings.json`:

```json
[
  {
    "name": "DEBUG",
    "value": "False"
  },
  {
    "name": "SECRET_KEY",
    "value": "your-secret-key-here"
  },
  {
    "name": "ALLOWED_HOSTS",
    "value": "myhealthcare-api.azurewebsites.net"
  },
  {
    "name": "DATABASE_URL",
    "value": "postgresql://user:pass@host:5432/db"
  }
]
```

---

## Cấu trúc File quan trọng

### 1. `.deployment` (Root folder)
Chỉ định project folder cho Azure:
```
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
project = backend
```

### 2. `backend/startup.sh`
Script chạy khi start application:
```bash
#!/bin/bash
python manage.py migrate --no-input
python manage.py collectstatic --no-input
gunicorn --bind=0.0.0.0 --timeout 600 myhealthcare.wsgi:application
```

### 3. `backend/requirements.txt`
Dependencies của Python

### 4. `backend/runtime.txt`
Phiên bản Python:
```
python-3.11.9
```

---

## Troubleshooting

### 1. Check logs

```bash
az webapp log tail \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api
```

### 2. SSH vào container

```bash
az webapp ssh \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api
```

### 3. Restart app

```bash
az webapp restart \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api
```

### 4. Xem configuration

```bash
az webapp config show \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api
```

---

## Database Setup (Azure PostgreSQL)

### Tạo PostgreSQL Database

```bash
# Tạo PostgreSQL server
az postgres flexible-server create \
  --resource-group myhealthcare-rg \
  --name myhealthcare-db-server \
  --location "Southeast Asia" \
  --admin-user myadmin \
  --admin-password <secure-password> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14

# Tạo database
az postgres flexible-server db create \
  --resource-group myhealthcare-rg \
  --server-name myhealthcare-db-server \
  --database-name myhealthcare

# Allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group myhealthcare-rg \
  --name myhealthcare-db-server \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Connection String

```
DATABASE_URL=postgresql://myadmin:<password>@myhealthcare-db-server.postgres.database.azure.com:5432/myhealthcare?sslmode=require
```

---

## Monitoring

### Enable Application Insights

```bash
az monitor app-insights component create \
  --app myhealthcare-insights \
  --location "Southeast Asia" \
  --resource-group myhealthcare-rg \
  --application-type web

# Link to web app
az webapp config appsettings set \
  --resource-group myhealthcare-rg \
  --name myhealthcare-api \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="<connection-string>"
```

---

## Cost Optimization

- **Free Tier**: F1 (free, limited resources)
- **Basic Tier**: B1 (~$13/month, recommended for dev/test)
- **Standard Tier**: S1 (~$70/month, recommended for production)

```bash
# Để dùng Free tier:
az appservice plan create \
  --name myhealthcare-plan \
  --resource-group myhealthcare-rg \
  --sku F1 \
  --is-linux
```

---

## Links hữu ích

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Deploy Python to Azure](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [Django on Azure](https://docs.microsoft.com/en-us/azure/app-service/configure-language-python)

