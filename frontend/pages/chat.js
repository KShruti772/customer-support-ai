import { useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { AuthContext } from './_app'
import withAuth from '../lib/withAuth'
import * as api from '../lib/api'
import Header from '../components/Header'
import ConversationSidebar from '../components/ConversationSidebar'
import ChatWindow from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'
import ErrorBanner from '../components/ErrorBanner'

function createMessage(role, content, extras = {}) {
    const id = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
    return {
        id,
        role,
        content,
        timestamp: new Date(),
        ...extras,
    }
}

function validateChatResponse(data) {
    if (
        !data ||
        typeof data.session_id !== 'string' ||
        typeof data.answer !== 'string' ||
        typeof data.escalate !== 'boolean' ||
        !Array.isArray(data.sources)
    ) {
        throw new Error('Malformed chat response')
    }
}

function getChatErrorMessage(error) {
    if (error.message === 'Malformed chat response') {
        return 'The support service returned an unexpected response. Please try again.'
    }

    if (!error.response) {
        return 'We could not reach the support service. Check your connection and try again.'
    }

    const status = error.response.status

    if (status === 401) {
        return 'Your session has expired. Redirecting to sign in.'
    }

    if (status === 404) {
        return 'This chat session is no longer available. Start a new chat and try again.'
    }

    if (status >= 400 && status < 500) {
        return 'We could not send that message. Review it and try again.'
    }

    return 'The support service is temporarily unavailable. Please try again shortly.'
}

function ChatPage() {
    const { user, logout } = useContext(AuthContext)
    const router = useRouter()
    const [messages, setMessages] = useState([])
    const [sessionId, setSessionId] = useState(null)
    const [isSending, setIsSending] = useState(false)
    const [error, setError] = useState(null)
    const [isSidebarOpen, setIsSidebarOpen] = useState(false)

    // Conversation list state
    const [conversations, setConversations] = useState([])
    const [loadingConversations, setLoadingConversations] = useState(true)
    const [conversationError, setConversationError] = useState(null)
    const [loadingHistory, setLoadingHistory] = useState(false)

    // Handle session_id from query parameter (when navigating from /conversations page)
    useEffect(() => {
        const loadSessionFromQuery = async () => {
            if (!router.isReady) return
            if (!router.query.session_id) return

            const querySessionId = router.query.session_id
            if (sessionId === querySessionId) return // Already loaded

            setError(null)
            setLoadingHistory(true)
            setMessages([])

            try {
                const data = await api.getHistory(querySessionId)
                const historyMessages = (data.messages || []).map((msg) =>
                    createMessage(msg.sender === 'user' ? 'user' : 'assistant', msg.text, {
                        timestamp: new Date(msg.timestamp),
                        escalate: msg.sender !== 'user' ? false : undefined,
                        sources: msg.sender !== 'user' ? [] : undefined,
                    })
                )
                setMessages(historyMessages)
                setSessionId(querySessionId)
            } catch (err) {
                console.error('Failed to load history:', err)
                setError('Could not load conversation. Please try again.')
                setLoadingHistory(false)
            } finally {
                setLoadingHistory(false)
            }
        }

        loadSessionFromQuery()
    }, [router.isReady, router.query.session_id])

    // Load conversations on mount
    useEffect(() => {
        const loadConversations = async () => {
            if (!user?.id) return

            setLoadingConversations(true)
            setConversationError(null)

            try {
                const data = await api.getConversationsForUser(user.id)
                // Sort by created_at descending (newest first)
                const sorted = (data.conversations || []).sort((a, b) => {
                    return new Date(b.created_at) - new Date(a.created_at)
                })
                setConversations(sorted)
            } catch (err) {
                console.error('Failed to load conversations:', err)
                setConversationError('Could not load conversations')
            } finally {
                setLoadingConversations(false)
            }
        }

        loadConversations()
    }, [user?.id])

    const handleSelectConversation = async (selectedSessionId) => {
        if (selectedSessionId === sessionId) return // Already selected
        if (isSending) return

        setError(null)
        setLoadingHistory(true)
        setMessages([])

        try {
            const data = await api.getHistory(selectedSessionId)
            const historyMessages = (data.messages || []).map((msg) =>
                createMessage(msg.sender === 'user' ? 'user' : 'assistant', msg.text, {
                    timestamp: new Date(msg.timestamp),
                    escalate: msg.sender !== 'user' ? false : undefined,
                    sources: msg.sender !== 'user' ? [] : undefined,
                })
            )
            setMessages(historyMessages)
            setSessionId(selectedSessionId)
            setIsSidebarOpen(false)
        } catch (err) {
            console.error('Failed to load history:', err)
            setError('Could not load conversation history')
            setLoadingHistory(false)
        } finally {
            setLoadingHistory(false)
        }
    }

    const handleSend = async (rawMessage) => {
        const text = rawMessage.trim()
        if (!text || isSending) return

        setError(null)
        setMessages((current) => [...current, createMessage('user', text)])
        setIsSending(true)

        try {
            const data = await api.sendChat(text, sessionId)
            validateChatResponse(data)

            const newSessionId = data.session_id
            const isNewSession = !sessionId

            setSessionId(newSessionId)
            setMessages((current) => [
                ...current,
                createMessage('assistant', data.answer, {
                    escalate: data.escalate,
                    sources: data.sources,
                }),
            ])

            // If new session, add to conversations list
            if (isNewSession) {
                const newConversation = {
                    session_id: newSessionId,
                    user_id: user.id,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    messages: [
                        { sender: 'user', text, timestamp: new Date().toISOString() },
                        { sender: 'assistant', text: data.answer, timestamp: new Date().toISOString() },
                    ],
                }
                setConversations((prev) => [newConversation, ...prev])
            }
        } catch (err) {
            if (err.response?.status === 404) {
                setSessionId(null)
            }
            setError(getChatErrorMessage(err))
        } finally {
            setIsSending(false)
        }
    }

    const handleNewChat = () => {
        if (isSending) return
        setMessages([])
        setSessionId(null)
        setError(null)
        setIsSidebarOpen(false)
        setLoadingHistory(false)
    }

    return (
        <div className="relative left-1/2 flex h-[calc(100vh-3rem)] min-h-[640px] w-[calc(100vw-2rem)] max-w-[1280px] -translate-x-1/2 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
            <ConversationSidebar
                sessionId={sessionId}
                messageCount={messages.length}
                onNewChat={handleNewChat}
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
                disabled={isSending}
                conversations={conversations}
                onSelectConversation={handleSelectConversation}
                loadingConversations={loadingConversations}
                conversationError={conversationError}
            />

            <div className="flex min-w-0 flex-1 flex-col">
                <Header
                    user={user}
                    onLogout={logout}
                    onOpenSidebar={() => setIsSidebarOpen(true)}
                />
                <ErrorBanner message={error} onDismiss={() => setError(null)} />

                {loadingHistory ? (
                    <div className="flex flex-1 items-center justify-center bg-gray-50">
                        <div className="text-center">
                            <p className="text-gray-600">Loading conversation...</p>
                        </div>
                    </div>
                ) : (
                    <ChatWindow messages={messages} isSending={isSending} />
                )}

                <ChatInput onSend={handleSend} disabled={isSending || loadingHistory} />
            </div>
        </div>
    )
}

export default withAuth(ChatPage)
