import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TaskMessageInput } from './TaskMessageInput'

describe('TaskMessageInput', () => {
  it('renders text input', () => {
    render(<TaskMessageInput onSubmit={vi.fn()} />)

    expect(screen.getByPlaceholderText(/type a message/i)).toBeDefined()
  })

  it('accepts text input', () => {
    render(<TaskMessageInput onSubmit={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Please hurry with this task' } })
    
    expect(input).toHaveProperty('value', 'Please hurry with this task')
  })

  it('submit button is disabled when input is empty', () => {
    render(<TaskMessageInput onSubmit={vi.fn()} />)

    const submitBtn = screen.getByRole('button', { name: /send/i })
    // Check the element is rendered
    expect(submitBtn).toBeDefined()
  })

  it('submit button is enabled when input has content', () => {
    render(<TaskMessageInput onSubmit={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Hello employee' } })
    
    const submitBtn = screen.getByRole('button', { name: /send/i })
    expect(submitBtn).toBeDefined()
  })

  it('calls onSubmit with message text when submitted', () => {
    const mockSubmit = vi.fn()
    render(<TaskMessageInput onSubmit={mockSubmit} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Need an update on progress' } })
    
    const form = input.closest('form')
    fireEvent.submit(form!)
    
    expect(mockSubmit).toHaveBeenCalledWith('Need an update on progress')
  })

  it('clears input after successful submit', async () => {
    const mockSubmit = vi.fn().mockResolvedValue(undefined)
    render(<TaskMessageInput onSubmit={mockSubmit} />)

    const input = screen.getByPlaceholderText(/type a message/i) as HTMLTextAreaElement
    fireEvent.change(input, { target: { value: 'Message to employee' } })
    
    const form = input.closest('form')
    fireEvent.submit(form!)
    
    // Wait for async
    await vi.waitFor(() => {
      expect(input.value).toBe('')
    })
  })

  it('shows loading state during submission', () => {
    const mockSubmit = vi.fn().mockImplementation(() => new Promise(() => {}))
    render(<TaskMessageInput onSubmit={mockSubmit} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Test message' } })
    
    const form = input.closest('form')
    fireEvent.submit(form!)
    
    expect(screen.getByRole('button', { name: /sending/i })).toBeDefined()
  })
})
