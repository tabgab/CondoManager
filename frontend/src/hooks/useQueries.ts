import { useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import type { 
  Building, 
  Report, ReportFilters,
  Task, TaskFilters,
  User,
  PaginatedResponse 
} from '../types'

// Query keys
export const queryKeys = {
  buildings: ['buildings'] as const,
  reports: (filters?: ReportFilters) => ['reports', filters] as const,
  tasks: (filters?: TaskFilters) => ['tasks', filters] as const,
  users: ['users'] as const,
  stats: ['stats'] as const,
}

// Buildings hook
export function useBuildings() {
  return useQuery<Building[]>({
    queryKey: queryKeys.buildings,
    queryFn: async () => {
      const response = await api.get<{ items: Building[] }>('/buildings')
      return response.items
    },
  })
}

// Reports hook with optional filters
export function useReports(filters?: ReportFilters) {
  const queryClient = useQueryClient()
  
  return useQuery<PaginatedResponse<Report>>({
    queryKey: queryKeys.reports(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('skip', '0')
      params.append('limit', '20')
      
      if (filters?.status) params.append('status', filters.status)
      if (filters?.priority) params.append('priority', filters.priority)
      if (filters?.building_id) params.append('building_id', filters.building_id)
      if (filters?.reporter_id) params.append('reporter_id', filters.reporter_id)
      
      const queryString = params.toString()
      const response = await api.get<PaginatedResponse<Report>>(`/reports?${queryString}`)
      return response
    },
  })
}

// Tasks hook with optional filters
export function useTasks(filters?: TaskFilters) {
  return useQuery<PaginatedResponse<Task>>({
    queryKey: queryKeys.tasks(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('skip', '0')
      params.append('limit', '20')
      
      if (filters?.status) params.append('status', filters.status)
      if (filters?.priority) params.append('priority', filters.priority)
      if (filters?.assignee_id) params.append('assignee_id', filters.assignee_id)
      if (filters?.building_id) params.append('building_id', filters.building_id)
      
      const queryString = params.toString()
      const response = await api.get<PaginatedResponse<Task>>(`/tasks?${queryString}`)
      return response
    },
  })
}

// Users hook
export function useUsers() {
  return useQuery<PaginatedResponse<User>>({
    queryKey: queryKeys.users,
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<User>>('/users')
      return response
    },
  })
}

// Dashboard stats hook
export function useDashboardStats() {
  return useQuery<{
    pending_reports: number
    active_tasks: number
    total_users: number
  }>({
    queryKey: queryKeys.stats,
    queryFn: async () => {
      // This would be a real endpoint in production
      // For now, return mock data or aggregate from other queries
      return {
        pending_reports: 0,
        active_tasks: 0,
        total_users: 0,
      }
    },
  })
}
