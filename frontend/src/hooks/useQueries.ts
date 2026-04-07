import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import type { 
  Building, 
  Report, ReportFilters,
  Task, TaskFilters,
  User,
  PaginatedResponse,
  TaskUpdate
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
      return response.data.items
    },
  })
}

// Reports hook with optional filters
export function useReports(filters?: ReportFilters) {
  return useQuery<PaginatedResponse<Report>>({
    queryKey: queryKeys.reports(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('skip', '0')
      params.append('limit', '20')
      
      if (filters?.status) params.append('status', filters.status)
      if (filters?.priority) params.append('priority', filters.priority)
      if (filters?.building_id) params.append('building_id', filters.building_id)
      if (filters?.submitted_by_id) params.append('submitted_by_id', filters.submitted_by_id)
      
      const queryString = params.toString()
      const response = await api.get<PaginatedResponse<Report>>(`/reports?${queryString}`)
      return response.data
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
      return response.data
    },
  })
}

// Users hook
export function useUsers() {
  return useQuery<PaginatedResponse<User>>({
    queryKey: queryKeys.users,
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<User>>('/users')
      return response.data
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

// Employee-specific task hooks
export function useMyAssignedTasks() {
  return useQuery<PaginatedResponse<Task>>({
    queryKey: ['tasks', 'my-assigned'],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Task>>('/tasks?assignee_id=me')
      return response.data
    },
  })
}

export function useUpdateTaskStatus() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ taskId, status }: { taskId: string; status: string }) => {
      const response = await api.patch<Task>(`/tasks/${taskId}/status`, { status })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

export function useAddTaskUpdate() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ taskId, content, isConcern }: { taskId: string; content: string; isConcern: boolean }) => {
      const response = await api.post<TaskUpdate>(`/tasks/${taskId}/updates`, {
        content,
        update_type: isConcern ? 'concern' : 'comment',
      })
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.taskId, 'updates'] })
    },
  })
}

// Task detail and messaging hooks
const TASK_DETAIL_KEY = 'task-detail'
const TASK_MESSAGES_KEY = 'task-messages'

export function useTaskDetail(id: string | null) {
  return useQuery<Task | null>({
    queryKey: [TASK_DETAIL_KEY, id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.get<Task>(`/tasks/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useTaskMessages(taskId: string | null) {
  return useQuery<TaskUpdate[]>({
    queryKey: [TASK_MESSAGES_KEY, taskId],
    queryFn: async () => {
      if (!taskId) return []
      const response = await api.get<TaskUpdate[]>(`/tasks/${taskId}/updates`)
      return response.data
    },
    enabled: !!taskId,
  })
}

export function useReassignTask() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ taskId, assigneeId }: { taskId: string; assigneeId: string }) => {
      const response = await api.patch<Task>(`/tasks/${taskId}`, { assignee_id: assigneeId })
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: [TASK_DETAIL_KEY, variables.taskId] })
    },
  })
}

export function useUnassignTask() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ taskId }: { taskId: string }) => {
      const response = await api.patch<Task>(`/tasks/${taskId}`, { assignee_id: null })
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: [TASK_DETAIL_KEY, variables.taskId] })
    },
  })
}

export function useVerifyTask() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ taskId }: { taskId: string }) => {
      const response = await api.patch<Task>(`/tasks/${taskId}/status`, { status: 'verified' })
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: [TASK_DETAIL_KEY, variables.taskId] })
    },
  })
}

export function useAddTaskMessage() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ taskId, content }: { taskId: string; content: string }) => {
      const response = await api.post<TaskUpdate>(`/tasks/${taskId}/updates`, {
        content,
        update_type: 'comment',
      })
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [TASK_MESSAGES_KEY, variables.taskId] })
      queryClient.invalidateQueries({ queryKey: [TASK_DETAIL_KEY, variables.taskId] })
    },
  })
}

// Apartments hook for a specific building
export function useApartments(buildingId: string | null) {
  return useQuery<any[]>({
    queryKey: ['apartments', buildingId],
    queryFn: async () => {
      if (!buildingId) return []
      const response = await api.get<{ items: any[] }>(`/apartments?building_id=${buildingId}`)
      return response.data.items
    },
    enabled: !!buildingId,
  })
}

// Create building mutation
export function useCreateBuilding() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: { name: string; address: string; city: string; manager_id?: string; country?: string; description?: string }) => {
      const response = await api.post<any>('/buildings', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.buildings })
    },
  })
}

// Create apartment mutation
export function useCreateApartment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: { building_id: string; unit_number: string; floor?: number; owner_id?: string; tenant_id?: string; description?: string }) => {
      const response = await api.post<any>('/apartments', data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['apartments', variables.building_id] })
    },
  })
}

// Update apartment mutation (for assigning owner/tenant)
export function useUpdateApartment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ apartmentId, buildingId, ...data }: { apartmentId: string; buildingId: string; owner_id?: string | null; tenant_id?: string | null }) => {
      const response = await api.patch<any>(`/apartments/${apartmentId}`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['apartments', variables.buildingId] })
    },
  })
}

// Add user to apartment mutation
export function useAddApartmentUser(apartmentId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: { user_id: string; role: string }) => {
      const response = await api.post<any>(`/apartments/${apartmentId}/users`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apartments'] })
    },
  })
}

// Remove user from apartment mutation
export function useRemoveApartmentUser(apartmentId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ userId, role }: { userId: string; role: string }) => {
      const response = await api.delete(`/apartments/${apartmentId}/users/${userId}?role=${role}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apartments'] })
    },
  })
}
