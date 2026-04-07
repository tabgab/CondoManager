import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ReportDetailModal } from './ReportDetailModal'
import type { Report } from '../../types'

const mockReport: Report = {
  id: 'r1',
  title: 'Leaky faucet',
  description: 'Kitchen sink is leaking water',
  status: 'acknowledged',
  priority: 'high',
  category: 'maintenance',
  building_id: 'b1',
  apartment_id: 'a1',
  submitted_by_id: 'u1',
  created_at: '2024-01-01T10:00:00Z',
  updated_at: '2024-01-02T14:00:00Z',
  acknowledged_at: '2024-01-01T12:00:00Z',
}

describe('ReportDetailModal', () => {
  it('renders full report information', () => {
    render(<ReportDetailModal report={mockReport} isOpen onClose={vi.fn()} />)

    expect(screen.getByText(/leaky faucet/i)).toBeDefined()
    expect(screen.getByText(/kitchen sink is leaking/i)).toBeDefined()
    expect(screen.getByText(/high/i)).toBeDefined()
    expect(screen.getByText(/maintenance/i)).toBeDefined()
  })

  it('shows the timeline component', () => {
    render(<ReportDetailModal report={mockReport} isOpen onClose={vi.fn()} />)

    expect(screen.getByText(/current status/i)).toBeDefined()
    expect(screen.getByText(/acknowledged by manager/i)).toBeDefined()
  })

  it('shows messages section', () => {
    render(<ReportDetailModal report={mockReport} isOpen onClose={vi.fn()} />)

    expect(screen.getByText(/conversation/i)).toBeDefined()
    expect(screen.getByText(/no messages yet/i)).toBeDefined()
  })

  it('does not render when isOpen is false', () => {
    render(<ReportDetailModal report={mockReport} isOpen={false} onClose={vi.fn()} />)

    expect(screen.queryByText(/leaky faucet/i)).toBeNull()
  })

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn()
    render(<ReportDetailModal report={mockReport} isOpen onClose={onClose} />)

    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)

    expect(onClose).toHaveBeenCalled()
  })

  it('shows report ID and submission date', () => {
    render(<ReportDetailModal report={mockReport} isOpen onClose={vi.fn()} />)

    expect(screen.getByText(/report #r1/i)).toBeDefined()
    expect(screen.getByText(/january 1/i)).toBeDefined()
  })

  it('displays priority and status badges', () => {
    render(<ReportDetailModal report={mockReport} isOpen onClose={vi.fn()} />)

    expect(screen.getAllByText(/acknowledged/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/high/i).length).toBeGreaterThan(0)
  })
})
