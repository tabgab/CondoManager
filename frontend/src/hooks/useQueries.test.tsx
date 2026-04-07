import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useBuildings, useReports, useTasks, useUsers } from './useQueries'
import type { Building, Report, Task, User } from '../types'

// Mock the API client
vi.mock('../lib/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '../lib/api'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useQueries hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('useBuildings', () => {
    it('should fetch buildings', async () => {
      const mockBuildings: Building[] = [
        {
          id: '1',
          name: 'Building A',
          address: '123 Main St',
          city: 'New York',
          manager_id: undefined,
          country: 'USA',
          created_at: '2024-01-01',
        },
      ]

      vi.mocked(api.get).mockResolvedValueOnce({ items: mockBuildings })

      const { result } = renderHook(() => useBuildings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockBuildings)
    })

    it('should handle fetch error', async () => {
      vi.mocked(api.get).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useBuildings(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toBeDefined()
    })
  })

  describe('useReports', () => {
    it('should fetch reports without filters', async () => {
      const mockReports: Report[] = [
        {
          id: '1',
          title: 'Leaky faucet',
          description: 'Kitchen sink is leaking',
          status: 'pending',
          priority: 'normal',
          submitted_by_id: '1',
          reporter: { id: '1', email: 'test@test.com', first_name: 'Test', last_name: 'User', role: 'owner', is_active: true, created_at: '2024-01-01' },
          building_id: '1',
          messages: [],
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ]

      vi.mocked(api.get).mockResolvedValueOnce({ items: mockReports, total: 1 })

      const { result } = renderHook(() => useReports(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data?.items).toEqual(mockReports)
      expect(result.current.data?.total).toBe(1)
    })

    it('should apply status filter', async () => {
      const mockReports: Report[] = []
      vi.mocked(api.get).mockResolvedValueOnce({ items: mockReports, total: 0 })

      renderHook(() => useReports({ status: 'pending' }), {
        wrapper: createWrapper(),
      })

      expect(api.get).toHaveBeenCalledWith('/reports?skip=0&limit=20&status=pending')
    })
  })

  describe('useTasks', () => {
    it('should fetch tasks', async () => {
      const mockTasks: Task[] = [
        {
          id: '1',
          title: 'Fix door',
          description: 'Main entrance door needs repair',
          status: 'pending',
          priority: 'high',
          created_by_id: '1',
          created_by: { id: '1', email: 'manager@test.com', first_name: 'Manager', last_name: 'User', role: 'manager', is_active: true, created_at: '2024-01-01' },
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ]

      vi.mocked(api.get).mockResolvedValueOnce({ items: mockTasks, total: 1 })

      const { result } = renderHook(() => useTasks({ status: 'pending' }), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data?.items).toEqual(mockTasks)
    })
  })

  describe('useUsers', () => {
    it('should fetch users', async () => {
      const mockUsers: User[] = [
        {
          id: '1',
          email: 'user@test.com',
          first_name: 'Test',
          last_name: 'User',
          role: 'owner',
          is_active: true,
          created_at: '2024-01-01',
        },
      ]

      vi.mocked(api.get).mockResolvedValueOnce({ items: mockUsers, total: 1 })

      const { result } = renderHook(() => useUsers(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data?.items).toEqual(mockUsers)
    })
  })
})
