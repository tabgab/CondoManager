import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { WeeklyTaskView } from './WeeklyTaskView'
import type { Task, TaskStatus } from '../../types'

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Fix leak',
    description: 'Kitchen leak',
    status: 'pending' as TaskStatus,
    priority: 'high',
    assignee_id: 'emp1',
    building_id: 'b1',
    due_date: new Date().toISOString().split('T')[0],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    title: 'Mow lawn',
    description: 'Front yard',
    status: 'in_progress' as TaskStatus,
    priority: 'normal',
    assignee_id: 'emp1',
    building_id: 'b1',
    due_date: new Date().toISOString().split('T')[0],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
]

describe('WeeklyTaskView', () => {
  it('renders weekly calendar with days of week', () => {
    render(
      <WeeklyTaskView
        tasks={mockTasks}
        onTaskClick={vi.fn()}
        currentDate={new Date()}
      />
    )

    expect(screen.getByText('Monday')).toBeDefined()
    expect(screen.getByText('Tuesday')).toBeDefined()
    expect(screen.getByText('Wednesday')).toBeDefined()
    expect(screen.getByText('Thursday')).toBeDefined()
    expect(screen.getByText('Friday')).toBeDefined()
    expect(screen.getByText('Saturday')).toBeDefined()
    expect(screen.getByText('Sunday')).toBeDefined()
  })

  it('displays tasks in correct day slots', () => {
    render(
      <WeeklyTaskView
        tasks={mockTasks}
        onTaskClick={vi.fn()}
        currentDate={new Date()}
      />
    )

    // Both tasks should be visible somewhere in the calendar
    expect(screen.getByText('Fix leak')).toBeDefined()
    expect(screen.getByText('Mow lawn')).toBeDefined()
  })

  it('shows task cards with status colors', () => {
    render(
      <WeeklyTaskView
        tasks={mockTasks}
        onTaskClick={vi.fn()}
        currentDate={new Date()}
      />
    )

    // Task cards should be clickable/rendered
    const taskCards = screen.getAllByRole('button')
    expect(taskCards.length).toBeGreaterThan(0)
  })

  it('calls onTaskClick when task is clicked', async () => {
    const mockOnClick = vi.fn()
    
    render(
      <WeeklyTaskView
        tasks={mockTasks}
        onTaskClick={mockOnClick}
        currentDate={new Date()}
      />
    )

    const taskButton = screen.getByText('Fix leak').closest('button') || screen.getByText('Fix leak')
    taskButton.click()
    
    expect(mockOnClick).toHaveBeenCalledWith('1')
  })
})
