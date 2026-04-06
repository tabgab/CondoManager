import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { TaskAssignmentControls } from './TaskAssignmentControls'

const mockEmployees = [
  { id: 'emp1', first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
  { id: 'emp2', first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' },
  { id: 'emp3', first_name: 'Bob', last_name: 'Wilson', email: 'bob@example.com' },
]

describe('TaskAssignmentControls', () => {
  it('renders employee dropdown', () => {
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId={null}
        onAssign={vi.fn()}
        onUnassign={vi.fn()}
      />
    )

    expect(screen.getByLabelText(/assign to/i)).toBeDefined()
  })
  it('shows current assignee when assigned', () => {
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId="emp1"
        onAssign={vi.fn()}
        onUnassign={vi.fn()}
      />
    )

    expect(screen.getByText(/currently assigned to/i)).toBeDefined()
    // Use getByText with exact option for the assignee name in the display
    expect(screen.getByText((content) => content.includes('John') && content.includes('Doe'))).toBeDefined()
  })
  it('shows unassigned state when no assignee', () => {
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId={null}
        onAssign={vi.fn()}
        onUnassign={vi.fn()}
      />
    )

    expect(screen.getByText(/not assigned/i)).toBeDefined()
  })

  it('calls onAssign when employee selected and assign clicked', async () => {
    const onAssign = vi.fn()
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId={null}
        onAssign={onAssign}
        onUnassign={vi.fn()}
      />
    )

    const select = screen.getByLabelText(/assign to/i)
    fireEvent.change(select, { target: { value: 'emp2' } })

    const assignBtn = screen.getByRole('button', { name: /assign/i })
    fireEvent.click(assignBtn)

    await waitFor(() => {
      expect(onAssign).toHaveBeenCalledWith('emp2')
    })
  })

  it('calls onUnassign when unassign button clicked', () => {
    const onUnassign = vi.fn()
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId="emp1"
        onAssign={vi.fn()}
        onUnassign={onUnassign}
      />
    )

    const unassignBtn = screen.getByRole('button', { name: /unassign/i })
    fireEvent.click(unassignBtn)

    expect(onUnassign).toHaveBeenCalled()
  })

  it('disables assign button when no employee selected', () => {
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId={null}
        onAssign={vi.fn()}
        onUnassign={vi.fn()}
      />
    )

    const assignBtn = screen.getByRole('button', { name: /assign/i })
    expect(assignBtn).toBeDisabled()
  })

  it('disables assign button when same employee already assigned', () => {
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId="emp1"
        onAssign={vi.fn()}
        onUnassign={vi.fn()}
      />
    )

    // Select the already assigned employee
    const select = screen.getByLabelText(/assign to/i)
    fireEvent.change(select, { target: { value: 'emp1' } })

    const assignBtn = screen.getByRole('button', { name: /assign/i })
    expect(assignBtn).toBeDisabled()
  })

  it('shows loading state during assignment', () => {
    render(
      <TaskAssignmentControls
        employees={mockEmployees}
        currentAssigneeId={null}
        onAssign={vi.fn()}
        onUnassign={vi.fn()}
        isAssigning={true}
      />
    )

    expect(screen.getByText(/assigning/i)).toBeDefined()
  })
})
