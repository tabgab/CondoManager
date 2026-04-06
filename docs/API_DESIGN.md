# CondoManager - API Design

## Conventions
- Base URL: `/api/v1`
- Auth: `Authorization: Bearer <access_token>` on all protected routes
- Content-Type: `application/json` (multipart/form-data for file uploads)
- Errors: `{"detail": "message"}` with appropriate HTTP status codes
- Pagination: `?page=1&per_page=20` → `{"items": [...], "total": N, "page": P, "pages": P}`
- Timestamps: ISO 8601 UTC strings
- IDs: UUID v4 strings

## HTTP Status Codes Used
| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (no/invalid token) |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 422 | Unprocessable Entity (FastAPI validation) |
| 500 | Internal Server Error |

---

## Authentication

### POST /api/v1/auth/login
Public. Returns JWT tokens.
```json
// Request
{"email": "user@example.com", "password": "secret"}

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {"id": "uuid", "email": "...", "role": "manager", "first_name": "..."}
}
```

### POST /api/v1/auth/refresh
```json
// Request
{"refresh_token": "eyJ..."}
// Response 200: same as login
```

### POST /api/v1/auth/logout
Invalidates refresh token.

### POST /api/v1/auth/forgot-password
```json
{"email": "user@example.com"}
// Response 200: {"message": "If account exists, reset email sent"}
```

### POST /api/v1/auth/reset-password
```json
{"token": "reset-token-from-email", "new_password": "newpass"}
```

---

## Users

### GET /api/v1/users/me
Returns current authenticated user.

### PUT /api/v1/users/me
Update own profile (name, phone, notification_prefs).

### GET /api/v1/users
**Roles**: manager, super_admin
Query params: `role`, `is_active`, `building_id`, `search`

### POST /api/v1/users
**Roles**: manager, super_admin
Create and invite a user (sends welcome email).
```json
{
  "email": "emp@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "employee",
  "employee_type": "caretaker",
  "phone": "+36..."
}
// Response 201: user object
```

### GET /api/v1/users/{id}
### PUT /api/v1/users/{id}
### DELETE /api/v1/users/{id}
Soft-delete (sets is_active=false). **Roles**: manager, super_admin

---

## Buildings & Apartments

### GET /api/v1/buildings
### POST /api/v1/buildings
**Roles**: super_admin, manager
```json
{"name": "Sunrise Condos", "address": "123 Main St"}
```

### GET /api/v1/buildings/{id}
### PUT /api/v1/buildings/{id}
### DELETE /api/v1/buildings/{id}

### GET /api/v1/buildings/{id}/apartments
### POST /api/v1/buildings/{id}/apartments
```json
{"unit_number": "3B", "floor": 3, "notes": "Corner unit"}
```

### GET /api/v1/apartments/{id}
### PUT /api/v1/apartments/{id}
### DELETE /api/v1/apartments/{id}

### POST /api/v1/apartments/{id}/assign-user
```json
{"user_id": "uuid", "relationship": "owner", "is_primary": true}
```

### DELETE /api/v1/apartments/{id}/users/{user_id}

---

## Reports

### POST /api/v1/reports
**Roles**: owner, tenant
```json
{
  "title": "Broken pipe in bathroom",
  "description": "Water leaking from under the sink...",
  "apartment_id": "uuid"
}
// Response 201: report object with id
```

### GET /api/v1/reports
Role-filtered automatically:
- owner/tenant → only own reports
- employee → reports linked to their tasks
- manager → all reports for their building

Query params: `status`, `building_id`, `apartment_id`, `from_date`, `to_date`, `search`, `page`, `per_page`

### GET /api/v1/reports/{id}

### PUT /api/v1/reports/{id}/acknowledge
**Roles**: manager
```json
{"message": "Thank you, we will look into this."}
```

### PUT /api/v1/reports/{id}/reject
**Roles**: manager
```json
{"reason": "This issue was already reported and addressed."}
```

### DELETE /api/v1/reports/{id}
**Roles**: owner (own reports only)
```json
{"reason": "submitted_in_error", "note": "Optional extra detail"}
```

### GET /api/v1/reports/{id}/messages
### POST /api/v1/reports/{id}/messages
```json
{"message": "Reply text here", "is_internal": false}
// is_internal=true: manager-only note, not sent to owner
```

### POST /api/v1/reports/{id}/attachments
Multipart form upload. Returns attachment object with Cloudinary URL.
`Content-Type: multipart/form-data`
Field: `file` (image/jpeg, image/png, image/webp, application/pdf; max 10MB)

### GET /api/v1/reports/{id}/attachments

---

## Tasks

### POST /api/v1/tasks
**Roles**: manager
```json
{
  "title": "Fix bathroom pipe",
  "description": "Replace P-trap under sink in unit 3B",
  "report_id": "uuid-or-null",
  "building_id": "uuid",
  "apartment_id": "uuid-or-null",
  "assigned_to": "uuid",
  "priority": "high",
  "due_date": "2026-04-10"
}
```

### GET /api/v1/tasks
Role-filtered:
- employee → only assigned to them
- manager → all building tasks

Query params: `status`, `assigned_to`, `priority`, `building_id`, `from_date`, `to_date`, `is_recurring`, `search`, `page`, `per_page`

### GET /api/v1/tasks/{id}
### PUT /api/v1/tasks/{id}
Partial update. Role-based field access enforced.

### PUT /api/v1/tasks/{id}/assign
**Roles**: manager
```json
{"assigned_to": "uuid", "note": "Reassigned due to availability"}
```

### PUT /api/v1/tasks/{id}/start
**Roles**: employee (assigned only)
```json
{"note": "Starting now, estimated 2 hours"}
```

### PUT /api/v1/tasks/{id}/progress
**Roles**: employee (assigned only)
```json
{"progress_pct": 60, "note": "Pipe replaced, testing for leaks"}
```

### PUT /api/v1/tasks/{id}/complete
**Roles**: employee (assigned only)
```json
{"note": "Work completed, area cleaned up"}
```

### PUT /api/v1/tasks/{id}/approve
**Roles**: manager
```json
{"note": "Confirmed resolved by owner feedback"}
```

### PUT /api/v1/tasks/{id}/cancel
**Roles**: manager
```json
{"reason": "Task no longer needed"}
```

### GET /api/v1/tasks/{id}/history
Returns ordered list of task_updates.

---

## Task Concerns

### POST /api/v1/tasks/{id}/concerns
**Roles**: employee (assigned only)
```json
{
  "concern_type": "extra_resources",
  "description": "Need a pipe wrench and replacement P-trap. Can you order?"}
```

### GET /api/v1/tasks/{id}/concerns

### PUT /api/v1/tasks/{id}/concerns/{concern_id}/resolve
**Roles**: manager
```json
{"resolution_note": "Parts ordered, will arrive tomorrow"}
```

---

## Recurring Schedules

### GET /api/v1/schedules
**Roles**: manager
Query params: `assigned_to`, `is_active`, `building_id`

### POST /api/v1/schedules
**Roles**: manager
```json
{
  "title": "Weekly Lawn Mowing",
  "description": "Mow front and back lawns",
  "building_id": "uuid",
  "assigned_to": "uuid",
  "frequency": "weekly",
  "day_of_week": [1],
  "time_of_day": "09:00:00"
}
```

### GET /api/v1/schedules/{id}
### PUT /api/v1/schedules/{id}
### DELETE /api/v1/schedules/{id}

### PUT /api/v1/schedules/{id}/toggle
Enable/disable schedule.

---

## Notifications

### GET /api/v1/notifications
Query params: `is_read`, `type`, `page`, `per_page`

### PUT /api/v1/notifications/{id}/read
### PUT /api/v1/notifications/read-all

### WebSocket: /ws/notifications
Auth: `?token=<access_token>`
Server pushes: `{"type": "notification", "data": {...notification object}}`

---

## Ledger

### GET /api/v1/ledger
**Roles**: manager, super_admin
Query params: `event_type`, `actor_id`, `reference_type`, `reference_id`, `from_date`, `to_date`, `page`, `per_page`

---

## Reports & Analytics

### GET /api/v1/analytics/summary
**Roles**: manager
Query params: `building_id`, `from_date`, `to_date`
```json
// Response
{
  "open_reports": 5,
  "pending_tasks": 12,
  "completed_tasks_this_month": 34,
  "avg_task_completion_days": 2.4,
  "employee_workload": [{"user_id": "...", "name": "...", "active_tasks": 3}]
}
```

### GET /api/v1/analytics/tasks
**Roles**: manager
Detailed task stats with filters.

### GET /api/v1/analytics/export
**Roles**: manager
Query params: `type` (tasks|reports|ledger), `format` (csv|pdf), `from_date`, `to_date`

---

## Channel Configuration

### GET /api/v1/settings/channels
**Roles**: manager, super_admin

### PUT /api/v1/settings/channels/{channel}
```json
{"config": {...channel-specific config...}, "is_enabled": true}
```

### POST /api/v1/settings/channels/{channel}/test
Sends a test message/ping via the channel.

### GET /api/v1/settings/channels/telegram/webhook-url
Returns the webhook URL to register with BotFather.

### POST /api/v1/settings/channels/telegram/set-webhook
Triggers registration of the webhook with Telegram API.

---

## System Health

### GET /health
Public. `{"status": "ok", "version": "1.0.0"}`

### GET /api/v1/settings/system
**Roles**: super_admin
System-wide settings.
