// User types
export type UserRole = 'super_admin' | 'manager' | 'employee' | 'owner' | 'tenant';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  phone?: string;
  created_at: string;
}

// Building types
export interface Building {
  id: string;
  name: string;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  description?: string;
  created_at: string;
}

export interface BuildingCreate {
  name: string;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  description?: string;
}

export interface BuildingUpdate {
  name?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  description?: string;
}

// Apartment types
export interface Apartment {
  id: string;
  building_id: string;
  unit_number: string;
  floor?: number;
  size_sqm?: number;
  bedrooms?: number;
  bathrooms?: number;
  building?: Building;
  owners: User[];
  tenants: User[];
  created_at: string;
}

export interface ApartmentCreate {
  building_id: string;
  unit_number: string;
  floor?: number;
  size_sqm?: number;
  bedrooms?: number;
  bathrooms?: number;
  owner_ids?: string[];
  tenant_ids?: string[];
}

export interface ApartmentUpdate {
  unit_number?: string;
  floor?: number;
  size_sqm?: number;
  bedrooms?: number;
  bathrooms?: number;
  owner_ids?: string[];
  tenant_ids?: string[];
}

// Report types
export type ReportStatus = 'pending' | 'acknowledged' | 'task_created' | 'rejected' | 'resolved' | 'deleted';
export type ReportPriority = 'low' | 'normal' | 'high' | 'urgent';

export interface Report {
  id: string;
  title: string;
  description: string;
  status: ReportStatus;
  priority: ReportPriority;
  reporter_id: string;
  reporter: User;
  building_id?: string;
  building?: Building;
  apartment_id?: string;
  apartment?: Apartment;
  assigned_manager_id?: string;
  assigned_manager?: User;
  rejection_reason?: string;
  messages: ReportMessage[];
  created_at: string;
  updated_at: string;
}

export interface ReportMessage {
  id: string;
  report_id: string;
  sender_id: string;
  sender: User;
  content: string;
  is_internal: boolean;
  created_at: string;
}

export interface ReportCreate {
  title: string;
  description: string;
  priority?: ReportPriority;
  building_id?: string;
  apartment_id?: string;
}

export interface ReportFilters {
  status?: ReportStatus;
  priority?: ReportPriority;
  building_id?: string;
  reporter_id?: string;
}

// Task types
export type TaskStatus = 'pending' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled' | 'verified';
export type TaskPriority = 'low' | 'normal' | 'high' | 'urgent';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  created_by_id: string;
  created_by: User;
  assignee_id?: string;
  assignee?: User;
  building_id?: string;
  building?: Building;
  apartment_id?: string;
  apartment?: Apartment;
  report_id?: string;
  report?: Report;
  estimated_hours?: number;
  due_date?: string;
  completed_at?: string;
  verified_by_id?: string;
  verified_by?: User;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskUpdate {
  id: string;
  task_id: string;
  author_id: string;
  author: User;
  content: string;
  is_concern: boolean;
  requires_manager_attention: boolean;
  percentage_complete?: number;
  created_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  assignee_id?: string;
  building_id?: string;
  apartment_id?: string;
  report_id?: string;
  estimated_hours?: number;
  due_date?: string;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: string;
  building_id?: string;
}

// Pagination types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// Stats types
export interface DashboardStats {
  pending_reports: number;
  active_tasks: number;
  total_users: number;
  pending_tasks: number;
  completed_tasks_today: number;
}
