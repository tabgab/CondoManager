# CondoManager - Data Model

## Entity Relationship Overview

```
Building
  └── Apartment (many)
        └── ApartmentUser (many: owner/tenant linked to apartment)

User
  ├── role: super_admin | manager | employee | owner | tenant
  ├── Reports (submitted by owner/tenant)
  └── Tasks (assigned to employee)

Report
  ├── Attachments (photos/files)
  ├── Messages (thread between owner and manager)
  └── Task (derived from report)

Task
  ├── RecurringSchedule (for regular tasks)
  ├── StatusUpdates (ledger entries)
  └── Notifications (sent to relevant parties)

Ledger
  └── Event (all system events, immutable)
```

---

## Tables

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | Login identifier |
| phone | VARCHAR(50) | Optional, for WhatsApp/Telegram |
| password_hash | VARCHAR(255) | bcrypt |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| role | ENUM | super_admin, manager, employee, owner, tenant |
| employee_type | VARCHAR(100) | caretaker, cleaner, heating_maintenance, other (if role=employee) |
| is_active | BOOLEAN | default true |
| telegram_chat_id | VARCHAR(100) | Linked Telegram account |
| whatsapp_number | VARCHAR(50) | Linked WhatsApp number |
| notification_prefs | JSONB | {email, telegram, whatsapp, web_push} |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### buildings
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(255) | |
| address | TEXT | |
| manager_id | UUID FK users | Primary manager |
| created_at | TIMESTAMP | |

### apartments
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| building_id | UUID FK buildings | |
| unit_number | VARCHAR(50) | e.g. "3B", "12" |
| floor | INTEGER | |
| notes | TEXT | |

### apartment_users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| apartment_id | UUID FK apartments | |
| user_id | UUID FK users | |
| relationship | ENUM | owner, tenant |
| is_primary | BOOLEAN | Primary contact for apartment |
| from_date | DATE | |
| to_date | DATE | null = current |

### reports
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| title | VARCHAR(255) | Short description |
| description | TEXT | Full problem description |
| submitted_by | UUID FK users | owner/tenant |
| apartment_id | UUID FK apartments | |
| building_id | UUID FK buildings | |
| status | ENUM | pending, acknowledged, rejected, task_created, resolved, deleted |
| rejection_reason | TEXT | If rejected by manager |
| deletion_reason | ENUM | completed, submitted_in_error, other (if deleted by owner) |
| channel | ENUM | web, telegram, whatsapp, email |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### report_attachments
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| report_id | UUID FK reports | |
| file_url | TEXT | Cloudinary URL |
| file_name | VARCHAR(255) | |
| file_type | VARCHAR(50) | image/jpeg, image/png, etc. |
| file_size | INTEGER | bytes |
| uploaded_at | TIMESTAMP | |

### report_messages
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| report_id | UUID FK reports | |
| sender_id | UUID FK users | |
| message | TEXT | |
| is_internal | BOOLEAN | Manager-only note (not visible to owner) |
| created_at | TIMESTAMP | |

### tasks
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| title | VARCHAR(255) | |
| description | TEXT | |
| report_id | UUID FK reports | null if standalone/recurring |
| building_id | UUID FK buildings | |
| apartment_id | UUID FK apartments | null if building-wide |
| created_by | UUID FK users | manager who created |
| assigned_to | UUID FK users | employee assigned |
| status | ENUM | pending, in_progress, on_hold, completed, cancelled |
| priority | ENUM | low, normal, high, urgent |
| progress_pct | INTEGER | 0-100 |
| status_note | TEXT | Current status description |
| due_date | DATE | |
| started_at | TIMESTAMP | |
| completed_at | TIMESTAMP | |
| approved_at | TIMESTAMP | Manager sign-off |
| approved_by | UUID FK users | |
| is_recurring | BOOLEAN | |
| recurring_schedule_id | UUID FK recurring_schedules | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### task_updates
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| task_id | UUID FK tasks | |
| updated_by | UUID FK users | |
| update_type | ENUM | status_change, progress, concern, comment, completion, approval |
| old_status | VARCHAR(50) | |
| new_status | VARCHAR(50) | |
| progress_pct | INTEGER | |
| message | TEXT | |
| created_at | TIMESTAMP | |

### task_concerns
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| task_id | UUID FK tasks | |
| raised_by | UUID FK users | employee |
| concern_type | ENUM | extra_resources, extra_people, external_help, other |
| description | TEXT | |
| is_resolved | BOOLEAN | default false |
| resolved_by | UUID FK users | |
| resolved_at | TIMESTAMP | |
| created_at | TIMESTAMP | |

### recurring_schedules
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| title | VARCHAR(255) | e.g. "Weekly Lawn Mowing" |
| description | TEXT | |
| building_id | UUID FK buildings | |
| assigned_to | UUID FK users | employee |
| created_by | UUID FK users | manager |
| frequency | ENUM | daily, weekly, biweekly, monthly, custom |
| schedule_cron | VARCHAR(100) | Cron expression for custom |
| day_of_week | INTEGER[] | 0=Mon, 6=Sun |
| time_of_day | TIME | |
| is_active | BOOLEAN | |
| next_run | TIMESTAMP | |
| created_at | TIMESTAMP | |

### notifications
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK users | recipient |
| type | ENUM | report_submitted, report_acknowledged, report_rejected, task_assigned, task_updated, task_completed, task_concern, approval_needed |
| title | VARCHAR(255) | |
| body | TEXT | |
| reference_type | ENUM | report, task |
| reference_id | UUID | FK to report or task |
| channel | ENUM | web, email, telegram, whatsapp |
| is_read | BOOLEAN | default false |
| sent_at | TIMESTAMP | |
| read_at | TIMESTAMP | |

### ledger_events
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| event_type | VARCHAR(100) | Namespaced: report.submitted, task.assigned, etc. |
| actor_id | UUID FK users | Who triggered the event |
| reference_type | VARCHAR(50) | report, task, user, etc. |
| reference_id | UUID | |
| payload | JSONB | Full event data snapshot |
| ip_address | VARCHAR(50) | |
| created_at | TIMESTAMP | Immutable |

### channel_configs
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| building_id | UUID FK buildings | |
| channel | ENUM | telegram, whatsapp, email, web_push |
| config | JSONB | Encrypted channel-specific config |
| is_enabled | BOOLEAN | |
| verified_at | TIMESTAMP | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### system_settings
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| building_id | UUID FK buildings | |
| key | VARCHAR(100) | Setting key |
| value | TEXT | Setting value |
| updated_by | UUID FK users | |
| updated_at | TIMESTAMP | |

---

## Key Indexes
```sql
-- Performance-critical lookups
CREATE INDEX idx_reports_submitted_by ON reports(submitted_by);
CREATE INDEX idx_reports_building_status ON reports(building_id, status);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_building_status ON tasks(building_id, status);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX idx_ledger_reference ON ledger_events(reference_type, reference_id);
CREATE INDEX idx_ledger_created ON ledger_events(created_at);
```

---

## Status State Machines

### Report Status Flow
```
pending → acknowledged → task_created → resolved
pending → rejected
[any owner-visible state] → deleted (by owner)
```

### Task Status Flow
```
pending → in_progress → completed → [manager approves] → approved
pending → cancelled
in_progress → on_hold → in_progress (concern raised/resolved)
```
