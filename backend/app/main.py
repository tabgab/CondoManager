from fastapi import FastAPI
from app.api import health, auth, users, buildings, apartments, reports, report_messages, tasks, task_updates, recurring_tasks, websocket, push_subscriptions, telegram

app = FastAPI()

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
