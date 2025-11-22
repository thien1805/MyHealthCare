# MyHealthCare Project

## Database Configuration

### Development (Local)

Có 2 cách cấu hình database cho development:

#### Cách 1: Sử dụng PostgreSQL service file (`.pg_service.conf`)

Thêm vào file `.env`:
```env
PGSERVICE=MyHealthCare_service
PGPASSFILE=~/.pgpass
```

#### Cách 2: Sử dụng thông tin database trực tiếp (Khuyến nghị)

Thêm vào file `.env`:
```env
DB_NAME=myhealthcare
DB_USER=postgres
DB_PASSWORD=your-local-password
DB_HOST=localhost
DB_PORT=5432
```

### Production (Deploy)

#### Azure PostgreSQL

Thêm vào environment variables trên Azure:
```env
AZURE_POSTGRESQL_CONNECTIONSTRING=postgresql://user:password@host:port/database
```

#### Other Cloud Platforms (Heroku, Railway, etc.)

Thêm vào environment variables:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

### Priority Order

Hệ thống sẽ ưu tiên theo thứ tự:
1. `AZURE_POSTGRESQL_CONNECTIONSTRING` (Azure)
2. `DATABASE_URL` (Generic cloud platforms)
3. Local development config (service file hoặc direct credentials)

