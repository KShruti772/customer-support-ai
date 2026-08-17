import { useState } from 'react'

export default function ChatInput({ onSend, disabled }) {
    const [value, setValue] = useState('')
    const canSend = value.trim().length > 0 && !disabled

    const submit = (event) => {
        event.preventDefault()
        if (!canSend) return
        onSend(value)
        setValue('')
    }

    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            submit(event)
        }
    }

    return (
        <form onSubmit={submit} className="border-t border-gray-200 bg-white p-4 sm:p-5">
            <label htmlFor="chat-message" className="sr-only">Message</label>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                <textarea
                    id="chat-message"
                    value={value}
                    onChange={(event) => setValue(event.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={2}
                    placeholder="Type your support question..."
                    disabled={disabled}
                    className="min-h-12 flex-1 resize-y rounded border border-gray-300 px-3 py-3 text-sm leading-5 text-gray-950 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
                <button
                    type="submit"
                    disabled={!canSend}
                    className="rounded bg-blue-700 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-gray-400"
                >
                    Send
                </button>
            </div>
            <p className="mt-2 text-xs text-gray-500">Press Enter to send. Press Shift+Enter for a new line.</p>
        </form>
    )
}
