import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TaskUpdateForm } from './TaskUpdateForm'

describe('TaskUpdateForm', () => {
  it('renders text input for progress description', () => {
    render(
      <TaskUpdateForm
        taskId="1"
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />
    )

    expect(screen.getByLabelText(/update description/i)).toBeDefined()
    expect(screen.getByPlaceholderText(/describe your progress/i)).toBeDefined()
  })

  it('renders concern checkbox', () => {
    render(
      <TaskUpdateForm
        taskId="1"
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />
    )

    expect(screen.getByLabelText(/need help/i)).toBeDefined()
  })

  it('submit button is disabled when description is empty', () => {
    render(
      <TaskUpdateForm
        taskId="1"
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />
    )

    const submitButton = screen.getByRole('button', { name: /submit update/i }) as HTMLButtonElement
    expect(submitButton.disabled).toBe(true)
  })

  it('enables submit button when description is filled', async () => {
    const user = userEvent.setup()

    render(
      <TaskUpdateForm
        taskId="1"
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />
    )

    await user.type(screen.getByLabelText(/update description/i), 'Made progress today')

    const submitButton = screen.getByRole('button', { name: /submit update/i }) as HTMLButtonElement
    expect(submitButton.disabled).toBe(false)
  })

  it('calls onSubmit with content and isConcern when form submitted', async () => {
    const user = userEvent.setup()
    const mockOnSubmit = vi.fn()

    render(
      <TaskUpdateForm
        taskId="1"
        onSubmit={mockOnSubmit}
        onCancel={vi.fn()}
        isLoading={false}
      />
    )

    await user.type(screen.getByLabelText(/update description/i), 'Made progress today')
    await user.click(screen.getByLabelText(/need help/i))

    const submitButton = screen.getByRole('button', { name: /submit update/i })
    await user.click(submitButton)

    expect(mockOnSubmit).toHaveBeenCalledWith('Made progress today', true)
  })

  it('calls onCancel when cancel button clicked', async () => {
    const user = userEvent.setup()
    const mockOnCancel = vi.fn()

    render(
      <TaskUpdateForm
        taskId="1"
        onSubmit={vi.fn()}
        onCancel={mockOnCancel}
        isLoading={false}
      />
    )

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('shows loading state when isLoading is true', () => {
    render(
      <TaskUpdateForm
        taskId="1"
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        isLoading={true}
      />
    )

    const submitButton = screen.getByRole('button', { name: /submitting/i }) as HTMLButtonElement
    expect(submitButton.disabled).toBe(true)
  })
})
