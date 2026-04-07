import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TaskDetail } from './TaskDetail'
import type { Task, TaskUpdate } from '../../types'

const mockTask: Task = {
  id: '1',
  title: 'Fix leak',
  description: 'Kitchen sink is leaking',
  status: 'in_progress',
  priority: 'high',
  assignee_id: 'emp1',
  building_id: 'b1',
  apartment_id: 'a1',
  due_date: '2024-01-15',
  estimated_hours: 2,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-10T00:00:00Z',
}

const mockUpdates: TaskUpdate[] = [
  {
    id: '1',
    task_id: '1',
    author_id: 'emp1',
    content: 'Started work on the leak',
    update_type: 'comment',
    created_at: '2024-01-10T00:00:00Z',
  },
]

describe('TaskDetail', () => {
  it('renders task information', () => {
    render(
      <TaskDetail
        task={mockTask}
        updates={mockUpdates}
        onClose={vi.fn()}
        onComplete={vi.fn()}
        onAddUpdate={vi.fn()}
        isLoading={false}
      />
    )

    expect(screen.getByText('Fix leak')).toBeDefined()
    expect(screen.getByText('Kitchen sink is leaking')).toBeDefined()
    expect(screen.getByText('in progress')).toBeDefined()
    expect(screen.getByText('high')).toBeDefined()
  })

  it('shows complete button for in_progress tasks', () => {
    render(
      <TaskDetail
        task={mockTask}
        updates={mockUpdates}
        onClose={vi.fn()}
        onComplete={vi.fn()}
        onAddUpdate={vi.fn()}
        isLoading={false}
      />
    )

    expect(screen.getByRole('button', { name: /mark complete/i })).toBeDefined()
  })

  it('does not show complete button for completed tasks', () => {
    const completedTask = { ...mockTask, status: 'completed' }
    render(
      <TaskDetail
        task={completedTask}
        updates={mockUpdates}
        onClose={vi.fn()}
        onComplete={vi.fn()}
        onAddUpdate={vi.fn()}
        isLoading={false}
      />
    )

    expect(screen.queryByRole('button', { name: /mark complete/i })).toBeNull()
  })

  it('shows task updates history', () => {
    render(
      <TaskDetail
        task={mockTask}
        updates={mockUpdates}
        onClose={vi.fn()}
        onComplete={vi.fn()}
        onAddUpdate={vi.fn()}
        isLoading={false}
      />
    )

    expect(screen.getByText('Started work on the leak')).toBeDefined()
  })

  it('calls onComplete when complete button clicked', async () => {
    const user = userEvent.setup()
    const mockOnComplete = vi.fn()

    render(
      <TaskDetail
        task={mockTask}
        updates={mockUpdates}
        onClose={vi.fn()}
        onComplete={mockOnComplete}
        onAddUpdate={vi.fn()}
        isLoading={false}
      />
    )

    const completeButton = screen.getByRole('button', { name: /mark complete/i })
    await user.click(completeButton)

    expect(mockOnComplete).toHaveBeenCalled()
  })

  it('calls onClose when close button clicked', async () => {
    const user = userEvent.setup()
    const mockOnClose = vi.fn()

    render(
      <TaskDetail
        task={mockTask}
        updates={mockUpdates}
        onClose={mockOnClose}
        onComplete={vi.fn()}
        onAddUpdate={vi.fn()}
        isLoading={false}
      />
    )

    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    expect(mockOnClose).toHaveBeenCalled()
  })
})
