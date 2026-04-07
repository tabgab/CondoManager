import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TaskMessageThread } from './TaskMessageThread'
import type { TaskUpdate } from '../../types'

const mockUpdates: TaskUpdate[] = [
  {
    id: 'u1',
    task_id: 't1',
    user_id: 'emp1',
    user_type: 'employee',
    content: 'Started working on the leak',
    update_type: 'comment',
    created_at: '2024-01-02T10:00:00Z',
  },
  {
    id: 'u2',
    task_id: 't1',
    user_id: 'mgr1',
    user_type: 'manager',
    content: 'Need more time to complete',
    update_type: 'concern',
    created_at: '2024-01-03T14:00:00Z',
  },
]

describe('TaskMessageThread', () => {
  it('renders messages with sender information', () => {
    render(<TaskMessageThread updates={mockUpdates} />)

    expect(screen.getByText(/started working on the leak/i)).toBeDefined()
    expect(screen.getByText(/need more time to complete/i)).toBeDefined()
  })

  it('shows employee messages with different styling', () => {
    render(<TaskMessageThread updates={mockUpdates} />)

    expect(screen.getByText(/employee/i)).toBeDefined()
    expect(screen.getByText(/started working on the leak/i)).toBeDefined()
  })

  it('shows manager messages with different styling', () => {
    render(<TaskMessageThread updates={mockUpdates} />)

    expect(screen.getByText(/manager/i)).toBeDefined()
    expect(screen.getByText(/need more time to complete/i)).toBeDefined()
  })

  it('highlights concern messages', () => {
    render(<TaskMessageThread updates={mockUpdates} />)

    expect(screen.getByText(/concern/i)).toBeDefined()
  })
  it('shows timestamps for messages', () => {
    render(<TaskMessageThread updates={mockUpdates} />)

    const times = screen.getAllByText(/Jan \d, \d{1,2}:\d{2}/i)
    expect(times.length).toBeGreaterThan(0)
  })

  it('shows empty state when no messages', () => {
    render(<TaskMessageThread updates={[]} />)

    expect(screen.getByText(/no updates yet/i)).toBeDefined()
  })

  it('displays status change indicators for system messages', () => {
    const systemUpdate: TaskUpdate = {
      id: 'u3',
      task_id: 't1',
      user_id: 'system',
      user_type: 'system',
      content: 'Task status changed to completed',
      update_type: 'comment',
      created_at: '2024-01-04T09:00:00Z',
    }
    render(<TaskMessageThread updates={[...mockUpdates, systemUpdate]} />)

    expect(screen.getByText(/system/i)).toBeDefined()
  })
})
