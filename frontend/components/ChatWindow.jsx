import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import LoadingIndicator from './LoadingIndicator'

export default function ChatWindow({ messages, isSending }) {
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }, [messages, isSending])

    return (
        <section className="flex min-h-0 flex-1 flex-col bg-gray-50" aria-label="Chat messages">
            <div className="border-b border-gray-200 bg-white px-4 py-4 sm:px-6">
                <p className="text-sm font-semibold text-gray-950">Support chat</p>
                <p className="mt-1 text-sm text-gray-500">Ask a question and the assistant will respond using the configured support backend.</p>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto px-4 py-5 sm:px-6">
                {messages.length === 0 ? (
                    <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center text-center">
                        <h2 className="text-2xl font-semibold text-gray-950">How can we help?</h2>
                        <p className="mt-3 text-sm leading-6 text-gray-600">
                            Ask about billing, products, technical issues, complaints, or general support.
                        </p>
                    </div>
                ) : (
                    <div className="mx-auto flex max-w-4xl flex-col gap-5">
                        {messages.map((message) => (
                            <MessageBubble key={message.id} message={message} />
                        ))}
                        {isSending && (
                            <div className="flex justify-start">
                                <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-sm">
                                    <LoadingIndicator />
                                </div>
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>
                )}
            </div>
        </section>
    )
}
