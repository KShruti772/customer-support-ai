import { useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { AuthContext } from './_app'
import withAuth from '../lib/withAuth'
import * as api from '../lib/api'
import Header from '../components/Header'
import ErrorBanner from '../components/ErrorBanner'

function ConversationsPage() {
    const { user, logout } = useContext(AuthContext)
    const router = useRouter()
    const [conversations, setConversations] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Load conversations on mount
    useEffect(() => {
        const loadConversations = async () => {
            if (!user?.id) return

            setLoading(true)
            setError(null)

            try {
                const data = await api.getConversationsForUser(user.id)
                // Sort by updated_at descending (most recently active first)
                const sorted = (data.conversations || []).sort((a, b) => {
                    return new Date(b.updated_at) - new Date(a.updated_at)
                })
                setConversations(sorted)
            } catch (err) {
                console.error('Failed to load conversations:', err)
                if (err.response?.status === 403) {
                    setError('You do not have permission to view conversations.')
                } else if (err.response?.status === 404) {
                    setError('Conversations not found.')
                } else if (!err.response) {
                    setError('Unable to reach the server. Please check your connection.')
                } else {
                    setError('Failed to load conversations. Please try again.')
                }
            } finally {
                setLoading(false)
            }
        }

        loadConversations()
    }, [user?.id])

    const handleNewConversation = () => {
        router.push('/chat')
    }

    const handleSelectConversation = (sessionId) => {
        router.push(`/chat?session_id=${encodeURIComponent(sessionId)}`)
    }

    const getConversationTitle = (conv) => {
        // If messages exist, use first user message as preview
        const userMessage = conv.messages?.find((m) => m.sender === 'user')
        if (userMessage) {
            const text = userMessage.text
            return text.length > 50 ? text.substring(0, 50) + '...' : text
        }
        return 'Untitled Conversation'
    }

    const formatDate = (dateString) => {
        const date = new Date(dateString)
        const now = new Date()

        // Today
        if (date.toDateString() === now.toDateString()) {
            return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
        }

        // Yesterday
        const yesterday = new Date(now)
        yesterday.setDate(yesterday.getDate() - 1)
        if (date.toDateString() === yesterday.toDateString()) {
            return 'Yesterday'
        }

        // This week
        const weekAgo = new Date(now)
        weekAgo.setDate(weekAgo.getDate() - 7)
        if (date > weekAgo) {
            return date.toLocaleDateString(undefined, { weekday: 'short' })
        }

        // Older
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    }

    return (
        <div className="flex h-screen flex-col bg-gray-50">
            <Header
                user={user}
                onLogout={logout}
                onOpenSidebar={() => { }}
            />

            <main className="flex-1 overflow-y-auto">
                <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
                    {/* Page Header */}
                    <div className="mb-8 flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Conversations</h1>
                            <p className="mt-2 text-gray-600">View and resume your support conversations</p>
                        </div>
                        <button
                            onClick={handleNewConversation}
                            className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        >
                            New Conversation
                        </button>
                    </div>

                    {/* Error Banner */}
                    <ErrorBanner message={error} onDismiss={() => setError(null)} />

                    {/* Loading State */}
                    {loading && (
                        <div className="flex min-h-96 items-center justify-center">
                            <div className="text-center">
                                <div className="mb-4 inline-block">
                                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600"></div>
                                </div>
                                <p className="text-gray-600">Loading conversations...</p>
                            </div>
                        </div>
                    )}

                    {/* Empty State */}
                    {!loading && conversations.length === 0 && !error && (
                        <div className="flex min-h-96 flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-white">
                            <svg
                                className="mb-4 h-16 w-16 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={1.5}
                                    d="M7 8h10M7 12h10M7 16h5M5 4h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2z"
                                />
                            </svg>
                            <h3 className="text-lg font-medium text-gray-900">No conversations yet</h3>
                            <p className="mt-1 text-gray-600">Start a new conversation to get support</p>
                            <button
                                onClick={handleNewConversation}
                                className="mt-4 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            >
                                Start New Conversation
                            </button>
                        </div>
                    )}

                    {/* Conversations List */}
                    {!loading && conversations.length > 0 && !error && (
                        <div className="space-y-3">
                            {conversations.map((conv) => (
                                <button
                                    key={conv.session_id}
                                    onClick={() => handleSelectConversation(conv.session_id)}
                                    className="w-full rounded-lg border border-gray-200 bg-white p-4 text-left transition-all hover:border-blue-300 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="min-w-0 flex-1">
                                            <h3 className="font-medium text-gray-900">
                                                {getConversationTitle(conv)}
                                            </h3>
                                            {conv.messages && conv.messages.length > 0 && (
                                                <p className="mt-1 text-sm text-gray-600">
                                                    {conv.messages.length} message{conv.messages.length === 1 ? '' : 's'}
                                                </p>
                                            )}
                                        </div>
                                        <div className="ml-4 flex-shrink-0 text-right">
                                            <p className="text-xs text-gray-500">
                                                {formatDate(conv.updated_at)}
                                            </p>
                                            <p className="mt-1 text-xs text-gray-400">
                                                Created {formatDate(conv.created_at)}
                                            </p>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}

export default withAuth(ConversationsPage)
