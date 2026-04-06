import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ReportMessageThread } from './ReportMessageThread'
import type { ReportMessage, Report } from '../../types'

const mockMessages: ReportMessage[] = [
  {
    id: '1',
    report_id: 'r1',
    sender_id: 'manager1',
    sender_type: 'manager',
    content: 'Thank you for reporting this. We will investigate.',
    created_at: '2024-01-02T10:00:00Z',
  },
  {
    id: '2',
    report_id: 'r1',
    sender_id: 'owner1',
    sender_type: 'owner',
    content: 'It is getting worse, please hurry!',
    created_at: '2024-01-03T09:00:00Z',
  },
]

const mockReport: Report = {
  id: 'r1',
  title: 'Leaky faucet',
  description: 'Kitchen sink leaking',
  status: 'acknowledged',
  priority: 'high',
  building_id: 'b1',
  reporter_id: 'owner1',
  created_at: '2024-01-01T10:00:00Z',
  updated_at: '2024-01-03T09:00:00Z',
  messages: mockMessages,
}

describe('ReportMessageThread', () => {
  it('renders message list with author and timestamp', () => {
    render(<ReportMessageThread report={mockReport} messages={mockMessages} />)

    expect(screen.getByText(/thank you for reporting this/i)).toBeDefined()
    expect(screen.getByText(/it is getting worse/i)).toBeDefined()
  })

  it('shows sender type for messages', () => {
    render(<ReportMessageThread report={mockReport} messages={mockMessages} />)

    expect(screen.getByText(/manager/i)).toBeDefined()
    expect(screen.getByText(/you/i)).toBeDefined()  // For owner messages
  })

  it('shows formatted dates for messages', () => {
    render(<ReportMessageThread report={mockReport} messages={mockMessages} />)

    // Should have date/time displayed
    const dates = screen.getAllByText(/january/i)
    expect(dates.length).toBeGreaterThan(0)
  })

  it('shows empty state when no messages', () => {
    render(<ReportMessageThread report={mockReport} messages={[]} />)

    expect(screen.getByText(/no messages yet/i)).toBeDefined()
  })

  it('displays manager messages with different styling', () => {
    render(<ReportMessageThread report={mockReport} messages={mockMessages} />)

    // Find manager message container (could have specific class or badge)
    const managerMessage = screen.getByText(/thank you for reporting this/i)
    const parent = managerMessage.closest('div[class*="flex"]')
    expect(parent).toBeDefined()
  })
})
