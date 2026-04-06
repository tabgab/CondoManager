import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MessageInput } from './MessageInput'

describe('MessageInput', () => {
  it('renders input field', () => {
    render(<MessageInput onSubmit={vi.fn()} />)

    expect(screen.getByPlaceholderText(/type a message/i)).toBeDefined()
  })

  it('accepts text input', () => {
    render(<MessageInput onSubmit={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Hello there' } })
    
    expect(input).toHaveProperty('value', 'Hello there')
  })

  it('shows character count', () => {
    render(<MessageInput onSubmit={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Test message' } })
    
    expect(screen.getByText(/12/i)).toBeDefined()
  })

  it('submit button is disabled when input is empty', () => {
    render(<MessageInput onSubmit={vi.fn()} />)

    const submitBtn = screen.getByRole('button', { name: /send/i })
    expect(submitBtn).toBeDisabled()
  })

  it('submit button is disabled when input only has whitespace', () => {
    render(<MessageInput onSubmit={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: '   ' } })
    
    const submitBtn = screen.getByRole('button', { name: /send/i })
    expect(submitBtn).toBeDisabled()
  })

  it('submit button is enabled when input has content', () => {
    render(<MessageInput onSubmit={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Hello' } })
    
    const submitBtn = screen.getByRole('button', { name: /send/i })
    expect(submitBtn).not.toBeDisabled()
  })

  it('calls onSubmit with message text when submitted', () => {
    const mockSubmit = vi.fn()
    render(<MessageInput onSubmit={mockSubmit} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Hello manager' } })
    
    const form = input.closest('form')
    fireEvent.submit(form!)
    
    expect(mockSubmit).toHaveBeenCalledWith('Hello manager')
  })

  it('clears input after successful submit', () => {
    const mockSubmit = vi.fn().mockResolvedValue(undefined)
    render(<MessageInput onSubmit={mockSubmit} />)

    const input = screen.getByPlaceholderText(/type a message/i) as HTMLTextAreaElement
    fireEvent.change(input, { target: { value: 'Test message' } })
    
    const form = input.closest('form')
    fireEvent.submit(form!)
    
    expect(input.value).toBe('')
  })

  it('shows loading state during submission', () => {
    const mockSubmit = vi.fn().mockImplementation(() => new Promise(() => {}))
    render(<MessageInput onSubmit={mockSubmit} />)

    const input = screen.getByPlaceholderText(/type a message/i)
    fireEvent.change(input, { target: { value: 'Test' } })
    
    const form = input.closest('form')
    fireEvent.submit(form!)
    
    const submitBtn = screen.getByRole('button', { name: /sending/i })
    expect(submitBtn).toBeDefined()
    expect(submitBtn).toBeDisabled()
  })
})
