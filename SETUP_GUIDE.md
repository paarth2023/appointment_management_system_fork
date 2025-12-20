# Setup & Run Guide

This guide covers how to run the Appointment Management System using Docker or locally.

---

## Prerequisites

- **Python 3.10+** (for local backend)
- **Node.js 18+** (for local frontend)
- **PostgreSQL** (or use Supabase/cloud PostgreSQL)
- **Docker & Docker Compose** (optional, for containerized setup)

---

## Option 1: Docker Setup (Recommended)

### Step 1: Configure Backend Environment

Create a `.env` file in `backend_django/` directory:

```bash
cd backend_django
touch .env
```

Add the following variables to `backend_django/.env`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database (PostgreSQL)
DB_NAME=appointment_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db  # Use 'localhost' for local PostgreSQL
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:80

# Email (Optional - for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twilio (Optional - for SMS/WhatsApp notifications)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Google Maps API (Optional - for location features)
GOOGLE_MAPS_API_KEY=your-google-api-key
```

**Note:** For Docker setup, you'll need to add a PostgreSQL service to `docker-compose.yml` or use an external database.

### Step 2: Update docker-compose.yml (Add Database)

If you want PostgreSQL in Docker, update `docker-compose.yml`:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    container_name: app_db
    environment:
      POSTGRES_DB: appointment_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  backend:
    build:
      context: ./backend_django
    container_name: app_backend
    env_file:
      - ./backend_django/.env
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./backend_django:/app
      - media_files:/app/media

  frontend:
    build:
      context: ./frontend/
    container_name: app_frontend
    depends_on:
      - backend
    ports:
      - "5173:80"
    restart: unless-stopped

volumes:
  postgres_data:
  media_files:
```

### Step 3: Build and Run

```bash
# From project root
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

---

## Option 2: Local Development Setup

### Backend Setup

#### 1. Navigate to backend directory

```bash
cd backend_django
```

#### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure environment

Create `.env` file in `backend_django/` (see environment variables above).

**For local PostgreSQL**, update `DB_HOST=localhost` in `.env`.

#### 5. Set up database

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

#### 6. Run development server

```bash
python manage.py runserver
```

Backend will run at **http://localhost:8000**

---

### Frontend Setup

#### 1. Navigate to frontend directory

```bash
cd frontend
```

#### 2. Install dependencies

```bash
npm install
```

#### 3. Configure API endpoint (if needed)

Check `frontend/src/services/api.js` - it should point to `http://localhost:8000/api`

#### 4. Run development server

```bash
npm run dev
```

Frontend will run at **http://localhost:5173**

---

## Quick Start Commands

### Docker (from project root)
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Local Development

**Terminal 1 - Backend:**
```bash
cd backend_django
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## Database Setup (PostgreSQL)

### Using Local PostgreSQL

1. Install PostgreSQL on your system
2. Create database:
   ```sql
   CREATE DATABASE appointment_db;
   CREATE USER postgres WITH PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE appointment_db TO postgres;
   ```
3. Update `.env` with local credentials

### Using Supabase (Cloud)

1. Create account at https://supabase.com
2. Create a new project
3. Get connection details from Project Settings → Database
4. Update `.env`:
   ```env
   DB_HOST=db.xxxxx.supabase.co
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your-supabase-password
   DB_PORT=5432
   ```

---

## Testing the Setup

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/api/
   ```

2. **Create a test user:**
   - Visit http://localhost:5173/signup
   - Or use API:
     ```bash
     curl -X POST http://localhost:8000/api/register/ \
       -H "Content-Type: application/json" \
       -d '{
         "email": "test@example.com",
         "full_name": "Test User",
         "password": "testpass123",
         "confirm_password": "testpass123",
         "role": "customer"
       }'
     ```

3. **Login:**
   ```bash
   curl -X POST http://localhost:8000/api/login/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpass123"
     }'
   ```

---

## Troubleshooting

### Backend Issues

- **Database connection error**: Check PostgreSQL is running and `.env` credentials are correct
- **Migration errors**: Run `python manage.py migrate --run-syncdb`
- **Port 8000 already in use**: Change port with `python manage.py runserver 8001`

### Frontend Issues

- **API connection errors**: Verify backend is running and CORS settings in `settings.py`
- **Module not found**: Run `npm install` again
- **Port 5173 already in use**: Vite will automatically use next available port

### Docker Issues

- **Build fails**: Check Dockerfile syntax and ensure all files are present
- **Container won't start**: Check logs with `docker-compose logs backend`
- **Database connection in Docker**: Ensure `DB_HOST=db` (service name) in `.env`

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Django secret key (generate with `openssl rand -hex 32`) |
| `DEBUG` | ✅ | Set to `True` for development |
| `ALLOWED_HOSTS` | ✅ | Comma-separated list of allowed hosts |
| `DB_NAME` | ✅ | PostgreSQL database name |
| `DB_USER` | ✅ | PostgreSQL username |
| `DB_PASSWORD` | ✅ | PostgreSQL password |
| `DB_HOST` | ✅ | Database host (`localhost` or `db` for Docker) |
| `DB_PORT` | ✅ | Database port (usually `5432`) |
| `EMAIL_HOST` | ❌ | SMTP server for email notifications |
| `EMAIL_PORT` | ❌ | SMTP port (usually `587`) |
| `EMAIL_HOST_USER` | ❌ | Email username |
| `EMAIL_HOST_PASSWORD` | ❌ | Email password/app password |
| `TWILIO_ACCOUNT_SID` | ❌ | Twilio account SID for SMS/WhatsApp |
| `TWILIO_AUTH_TOKEN` | ❌ | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | ❌ | Twilio phone number |
| `TWILIO_WHATSAPP_NUMBER` | ❌ | Twilio WhatsApp number |
| `GOOGLE_MAPS_API_KEY` | ❌ | Google Maps API key for location features |

---

## Next Steps

1. Create a superuser: `python manage.py createsuperuser`
2. Access admin panel: http://localhost:8000/admin
3. Create services and schedules as an organizer
4. Book appointments as a customer
5. Test notification system (requires email/Twilio setup)

---

**Need Help?** Check the main README.md for more project details.

