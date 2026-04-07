from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, auth, users, buildings, apartments, reports, report_messages, tasks, task_updates, recurring_tasks, websocket, push_subscriptions, telegram
from app.core.config import settings

app = FastAPI(
    title="CondoManager API",
    description="Condominium management platform API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS configuration - allows frontend from Vercel and local development
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "https://condomanager.vercel.app",
    "https://condo-manager-five.vercel.app",
    "https://condomanager-git-*.vercel.app",  # Vercel preview deployments
]

# Add custom origins from settings if available
if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
    custom_origins = [o.strip() for o in settings.CORS_ORIGINS.split(',') if o.strip()]
    origins.extend(custom_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print(f"🚀 CondoManager API starting up...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Allowed CORS origins: {origins}")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 CondoManager API shutting down...")
app.include_router(health.router, prefix="/health")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(buildings.router)
app.include_router(apartments.router)
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(report_messages.router, tags=["report_messages"])
app.include_router(tasks.router)
app.include_router(task_updates.router)
app.include_router(recurring_tasks.router)
app.include_router(websocket.router)
app.include_router(push_subscriptions.router)
app.include_router(telegram.router)
