import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ReportForm } from './ReportForm'

// Mock the hook
vi.mock('../../hooks/useReports', () => ({
  useCreateReport: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
    isSuccess: false,
    isError: false,
    error: null,
    reset: vi.fn(),
  }),
}))

describe('ReportForm', () => {
  const mockBuildings = [
    { id: '1', name: 'Building A', address: '123 Main St', city: 'NYC', postal_code: '10001', country: 'USA', created_at: '2024-01-01' },
    { id: '2', name: 'Building B', address: '456 Oak Ave', city: 'NYC', postal_code: '10002', country: 'USA', created_at: '2024-01-01' },
  ]

  const mockApartments = [
    { id: '1', building_id: '1', unit_number: '101', floor: 1, building: mockBuildings[0], owners: [], tenants: [], created_at: '2024-01-01' },
    { id: '2', building_id: '1', unit_number: '102', floor: 1, building: mockBuildings[0], owners: [], tenants: [], created_at: '2024-01-01' },
  ]

  it('renders form with all required fields', () => {
    render(
      <ReportForm
        buildings={mockBuildings}
        apartments={mockApartments}
        onSuccess={() => {}}
      />
    )

    expect(screen.getByLabelText(/title/i)).toBeDefined()
    expect(screen.getByLabelText(/description/i)).toBeDefined()
    expect(screen.getByLabelText(/category/i)).toBeDefined()
    expect(screen.getByLabelText(/priority/i)).toBeDefined()
    expect(screen.getByLabelText(/building/i)).toBeDefined()
    expect(screen.getByLabelText(/apartment/i)).toBeDefined()
    expect(screen.getByRole('button', { name: /submit report/i })).toBeDefined()
  })

  it('submit button is disabled when required fields are empty', () => {
    render(
      <ReportForm
        buildings={mockBuildings}
        apartments={mockApartments}
        onSuccess={() => {}}
      />
    )

    const submitButton = screen.getByRole('button', { name: /submit report/i }) as HTMLButtonElement
    expect(submitButton.disabled).toBe(true)
  })

  it('enables submit button when all required fields are filled', async () => {
    const user = userEvent.setup()

    render(
      <ReportForm
        buildings={mockBuildings}
        apartments={mockApartments}
        onSuccess={() => {}}
      />
    )

    await user.type(screen.getByLabelText(/title/i), 'Leaky faucet')
    await user.type(screen.getByLabelText(/description/i), 'Kitchen sink is leaking')
    await user.selectOptions(screen.getByLabelText(/category/i), 'maintenance')
    await user.selectOptions(screen.getByLabelText(/building/i), '1')

    const submitButton = screen.getByRole('button', { name: /submit report/i }) as HTMLButtonElement
    expect(submitButton.disabled).toBe(false)
  })

  it('calls onSuccess after successful submission', async () => {
    const user = userEvent.setup()
    const mockOnSuccess = vi.fn()

    render(
      <ReportForm
        buildings={mockBuildings}
        apartments={mockApartments}
        onSuccess={mockOnSuccess}
      />
    )

    await user.type(screen.getByLabelText(/title/i), 'Leaky faucet')
    await user.type(screen.getByLabelText(/description/i), 'Kitchen sink is leaking')
    await user.selectOptions(screen.getByLabelText(/category/i), 'maintenance')
    await user.selectOptions(screen.getByLabelText(/building/i), '1')

    const submitButton = screen.getByRole('button', { name: /submit report/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('shows loading state during submission', () => {
    render(
      <ReportForm
        buildings={mockBuildings}
        apartments={mockApartments}
        onSuccess={() => {}}
        isSubmitting={true}
      />
    )

    const submitButton = screen.getByRole('button', { name: /submitting/i }) as HTMLButtonElement
    expect(submitButton.disabled).toBe(true)
  })
})
