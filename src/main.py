from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from dependencies.auth_dependencies import get_current_user

from auth.get_client_token import router as client_token_router 
from auth.token_validation_router import router as token_validation_router
from auth.auth import router as auth_router
from routes.user_register import router as user_register_router
from routes.get_user_by_id import router as get_user_by_id_router
from routes.user_validation import router as user_validation_router
from routes.user_stations import router as user_stations_router
from routes.user_profile import router as user_profile_router
from routes.root_redirect import router as root_redirect_router
from routes.health import router as health_router


from aclimate_v3_orm_frontend.database.base import create_tables

# Create FastAPI app instance
app = FastAPI(
    title="Aclimate Users API",
    description="API for user authentication and registration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_auth = [Depends(get_current_user)]

# Include routers
# Public routers (no authentication)
app.include_router(root_redirect_router)
app.include_router(client_token_router)
app.include_router(token_validation_router)
app.include_router(auth_router)

# Protected routers (require valid user token)
app.include_router(user_register_router, dependencies=_auth)
app.include_router(get_user_by_id_router)
app.include_router(user_validation_router, dependencies=_auth)
app.include_router(user_stations_router, dependencies=_auth)
app.include_router(user_profile_router, dependencies=_auth)

# Health router (no authentication, excluded from OpenAPI schema)
app.include_router(health_router)

# Startup event to create tables
@app.on_event("startup")
def startup_event():
    print("🚀 Creando tablas al iniciar...")
    create_tables()
    print("✅ Tablas creadas exitosamente!")

#uvicorn main:app --reload
#uvicorn main:app --port 9000 --reload
