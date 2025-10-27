# 👥 AClimate V3 Frontend Users Web API

API for managing users, authentication, and weather station preferences for AClimate frontend applications.

## 🏷️ Version & Tags

![GitHub release (latest by date)](https://img.shields.io/github/v/release/CIAT-DAPA/aclimate_v3_frontend_users_webapi) ![](https://img.shields.io/github/v/tag/CIAT-DAPA/aclimate_v3_frontend_users_webapi)

---

## 📌 Introduction

The **AClimate V3 Frontend Users Web API** provides RESTful endpoints for managing user accounts, authentication, and user preferences for weather stations in the AClimate platform. Built with **FastAPI**, it integrates with **Keycloak** for secure authentication and authorization.

This API handles:
- User registration and validation
- User profile management
- Weather station preferences per user
- Integration with Keycloak for authentication
- Multi-app support (different countries/regions)

---

## ✨ Features

- 🚀 **FastAPI**-based high-performance REST API  
- 🔐 **Keycloak** integration for OAuth2 authentication and token validation
- 👤 User registration, validation, and profile management
- �️ Weather station preferences management (add, update, delete)
- 🌍 Multi-application support
- 🔑 Role-based authorization
- 🧩 Modular router structure  
- 📚 Auto-generated Swagger & ReDoc documentation  
- 🐳 Docker support for PostgreSQL database

---

## 📋 API Endpoints

### Authentication
- `POST /auth/get-client-token` - Get Keycloak token using client credentials
- `GET /auth/token/validate` - Validate a Keycloak token

### User Management
- `POST /validate/user` - Validate user and create if doesn't exist
- `POST /users/register` - Register a new user
- `GET /users/by-keycloak-id/{keycloak_id}` - Get user by Keycloak ID
- `GET /users/get-user/{user_id}` - Get user with client roles from Keycloak

### Weather Stations
- `GET /user-stations/{user_id}` - Get all weather stations for a user
- `POST /user-stations/{user_id}` - Add a weather station to user interests
- `PUT /user-stations/{user_id}/{ws_ext_id}` - Update notification settings
- `DELETE /user-stations/{user_id}/{ws_ext_id}` - Remove a weather station

---

## ✅ Requirements

- **Python** >= 3.10  
- **PostgreSQL** (via Docker or local installation)
- **Keycloak** for authentication and user management  
- **Docker** (optional, for containerized PostgreSQL)

### Python Dependencies
- FastAPI
- Pydantic
- SQLAlchemy
- psycopg2-binary
- python-dotenv
- uvicorn
- python-jose
- aclimate_v3_orm_frontend (custom ORM package)

---

## � Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/CIAT-DAPA/aclimate_v3_frontend_users_webapi.git
cd aclimate_v3_frontend_users_webapi
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🐳 Docker Setup

### Start PostgreSQL Database

```bash
docker run --name aclimate_frontend_users \
  --env=POSTGRES_PASSWORD=adminpass \
  --env=POSTGRES_DB=aclimate_frontend_users_db \
  --env=POSTGRES_USER=admin \
  -p 5433:5432 \
  -d postgres:latest
```

### Start Keycloak (optional)

```bash
docker run -d --name keycloak \
  -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

---

## 🌱 Environment Variables

Create a `.env` file in the `src` directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://admin:adminpass@localhost:5433/aclimate_frontend_users_db

# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
REALM_NAME=aclimate
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
```

---

## 🗄️ Database Setup

### Option 1: Automatic (on API startup)

The API will automatically create tables when it starts for the first time.

### Option 2: Manual Setup

Run the population script to create sample apps:

```bash
python create_apps.py
```

Or populate with sample data:

```bash
python populate_sample_data.py
```

---

## 🚀 Run the API

### Development Mode

```bash
cd src
uvicorn main:app --reload
```

### Custom Port

```bash
uvicorn main:app --port 9000 --reload
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📚 API Documentation

Once the API is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Authentication Flow

### 1. Get Client Token

```bash
POST /auth/get-client-token
Content-Type: application/json

{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret"
}
```

### 2. Use Token in Requests

```bash
GET /user-stations/1
Authorization: Bearer <access_token>
```

---

## � Database Schema

### Tables

- **apps** - Applications (countries/regions)
  - `id`, `name`, `country_ext_id`, `enable`, `register`, `updated`

- **users** - User accounts
  - `id`, `ext_key_clock_id`, `app_id`, `profile`, `enable`, `register`, `updated`

- **ws_interested** - User weather station preferences
  - `id`, `user_id`, `ws_ext_id`, `notification`, `enable`, `register`, `updated`

---

## 🛠️ Development

### Project Structure

```
aclimate_v3_frontend_users_webapi/
├── src/
│   ├── main.py                    # FastAPI application entry point
│   ├── auth/                      # Authentication modules
│   │   ├── auth.py
│   │   ├── get_client_token.py
│   │   └── token_validation_router.py
│   ├── routes/                    # API endpoints
│   │   ├── user_register.py
│   │   ├── user_validation.py
│   │   ├── get_user_by_id.py
│   │   └── user_stations.py
│   └── dependencies/              # Shared dependencies
│       └── auth_dependencies.py
├── create_apps.py                 # Script to populate apps
├── populate_sample_data.py        # Sample data script
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is part of the AClimate platform developed by CIAT-DAPA.

---

## � Authors

- **CIAT-DAPA Team**

---

## 📧 Support

For issues and questions, please open an issue on GitHub or contact the development team
