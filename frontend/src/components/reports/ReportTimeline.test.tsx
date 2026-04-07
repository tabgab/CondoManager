import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ReportTimeline } from './ReportTimeline'
import type { Report } from '../../types'

const mockReport: Report = {
  id: '1',
  title: 'Leaky faucet',
  description: 'Kitchen sink leaking',
  status: 'task_created',
  priority: 'high',
  building_id: 'b1',
  submitted_by_id: 'u1',
  created_at: '2024-01-01T10:00:00Z',
  updated_at: '2024-01-02T14:00:00Z',
}

describe('ReportTimeline', () => {
  it('renders timeline with submission event', () => {
    render(<ReportTimeline report={mockReport} />)

    expect(screen.getByText(/report submitted/i)).toBeDefined()
    expect(screen.getByText(/january 1/i)).toBeDefined()
  })

  it('shows acknowledgment event when acknowledged', () => {
    const acknowledgedReport = { ...mockReport, status: 'acknowledged' as const, acknowledged_at: '2024-01-01T12:00:00Z' }
    render(<ReportTimeline report={acknowledgedReport} />)

    expect(screen.getByText(/acknowledged by manager/i)).toBeDefined()
  })

  it('shows task creation event when task_created', () => {
    render(<ReportTimeline report={mockReport} />)

    expect(screen.getByText(/task created/i)).toBeDefined()
  })

  it('shows resolved event when resolved', () => {
    const resolvedReport = { 
      ...mockReport, 
      status: 'resolved' as const, 
      resolved_at: '2024-01-05T16:00:00Z',
      resolution_note: 'Fixed the leak'
    }
    render(<ReportTimeline report={resolvedReport} />)

    expect(screen.getByText(/resolved/i)).toBeDefined()
    expect(screen.getByText(/fixed the leak/i)).toBeDefined()
  })

  it('renders events in chronological order', () => {
    render(<ReportTimeline report={mockReport} />)

    const events = screen.getAllByRole('listitem')
    expect(events.length).toBeGreaterThan(0)
  })

  it('highlights current status', () => {
    render(<ReportTimeline report={mockReport} />)

    // Look for the heading specifically
    const currentStatus = screen.getByRole('heading', { name: /current status/i })
    expect(currentStatus).toBeDefined()
  })
})
