import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ManagerTaskDetail } from './ManagerTaskDetail'
import type { Task } from '../../types'

const mockTask: Task = {
  id: 't1',
  title: 'Fix leaking pipe',
  description: 'Kitchen sink pipe needs replacement',
  status: 'in_progress',
  priority: 'high',
  building_id: 'b1',
  apartment_id: 'a1',
  assignee_id: 'emp1',
  created_by_id: 'mgr1',
  created_at: '2024-01-01T10:00:00Z',
  updated_at: '2024-01-02T14:00:00Z',
  due_date: '2024-01-05T17:00:00Z',
  estimated_hours: 2,
}

const mockEmployees = [
  { id: 'emp1', first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
  { id: 'emp2', first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' },
]

describe('ManagerTaskDetail', () => {
  it('renders task information', () => {
    render(
      <ManagerTaskDetail
        task={mockTask}
        isOpen
        onClose={vi.fn()}
        employees={mockEmployees}
      />
    )

    expect(screen.getByText(/fix leaking pipe/i)).toBeDefined()
    expect(screen.getByText(/kitchen sink pipe needs replacement/i)).toBeDefined()
    expect(screen.getByText(/in_progress/i)).toBeDefined()
    expect(screen.getByText(/high/i)).toBeDefined()
  })

  it('shows assignment controls with current assignee', () => {
    render(
      <ManagerTaskDetail
        task={mockTask}
        isOpen
        onClose={vi.fn()}
        employees={mockEmployees}
      />
    )

    expect(screen.getByText(/assigned to/i)).toBeDefined()
    expect(screen.getByText(/john doe/i)).toBeDefined()
  })

  it('shows message thread section', () => {
    render(
      <ManagerTaskDetail
        task={mockTask}
        isOpen
        onClose={vi.fn()}
        employees={mockEmployees}
      />
    )

    expect(screen.getByText(/messages/i)).toBeDefined()
    expect(screen.getByText(/conversation with employee/i)).toBeDefined()
  })

  it('shows complete button for in_progress tasks', () => {
    render(
      <ManagerTaskDetail
        task={mockTask}
        isOpen
        onClose={vi.fn()}
        employees={mockEmployees}
      />
    )

    expect(screen.getByRole('button', { name: /mark as complete/i })).toBeDefined()
  })

  it('shows verify button for completed tasks', () => {
    const completedTask = { ...mockTask, status: 'completed' as const }
    render(
      <ManagerTaskDetail
        task={completedTask}
        isOpen
        onClose={vi.fn()}
        employees={mockEmployees}
      />
    )

    expect(screen.getByRole('button', { name: /verify/i })).toBeDefined()
  })

  it('calls onClose when close button clicked', () => {
    const onClose = vi.fn()
    render(
      <ManagerTaskDetail
        task={mockTask}
        isOpen
        onClose={onClose}
        employees={mockEmployees}
      />
    )

    const closeBtn = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeBtn)
    expect(onClose).toHaveBeenCalled()
  })

  it('shows due date and estimated hours', () => {
    render(
      <ManagerTaskDetail
        task={mockTask}
        isOpen
        onClose={vi.fn()}
        employees={mockEmployees}
      />
    )

    expect(screen.getByText(/due date/i)).toBeDefined()
    expect(screen.getByText(/estimated hours/i)).toBeDefined()
  })

  it('does not render when isOpen is false', () => {
    render(
      <ManagerTaskDetail
        task={mockTask}
        isOpen={false}
        onClose={vi.fn()}
        employees={mockEmployees}
      />
    )

    expect(screen.queryByText(/fix leaking pipe/i)).toBeNull()
  })
})
