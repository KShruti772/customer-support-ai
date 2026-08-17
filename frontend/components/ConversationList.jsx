export default function ConversationList({
    conversations,
    activeSessionId,
    onSelect,
    loading,
    error,
}) {
    if (loading) {
        return (
            <div className="border-b border-gray-800 p-4">
                <p className="text-sm text-gray-400">Loading conversations...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="border-b border-gray-800 p-4">
                <p className="text-sm text-red-400">Failed to load conversations</p>
            </div>
        )
    }

    if (!conversations || conversations.length === 0) {
        return (
            <div className="border-b border-gray-800 p-4">
                <p className="text-sm text-gray-500">No conversations yet</p>
            </div>
        )
    }

    // Group conversations by date
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const groups = {
        today: [],
        yesterday: [],
        older: [],
    }

    conversations.forEach((conv) => {
        const convDate = new Date(conv.created_at)
        convDate.setHours(0, 0, 0, 0)

        if (convDate.getTime() === today.getTime()) {
            groups.today.push(conv)
        } else if (convDate.getTime() === yesterday.getTime()) {
            groups.yesterday.push(conv)
        } else {
            groups.older.push(conv)
        }
    })

    const getConversationTitle = (conv) => {
        // If messages exist, use first user message as preview
        const userMessage = conv.messages?.find((m) => m.sender === 'user')
        if (userMessage) {
            const text = userMessage.text
            return text.length > 30 ? text.substring(0, 30) + '...' : text
        }
        return 'Conversation'
    }

    return (
        <div className="border-b border-gray-800">
            {groups.today.length > 0 && (
                <div>
                    <p className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Today</p>
                    <div className="space-y-1 px-2">
                        {groups.today.map((conv) => (
                            <button
                                key={conv.session_id}
                                onClick={() => onSelect(conv.session_id)}
                                className={`w-full rounded px-2 py-2 text-left text-sm transition-colors ${activeSessionId === conv.session_id
                                        ? 'bg-blue-600 text-white'
                                        : 'text-gray-300 hover:bg-gray-800'
                                    }`}
                            >
                                <p className="truncate">{getConversationTitle(conv)}</p>
                                <p className="text-xs text-gray-400 opacity-75">
                                    {new Date(conv.created_at).toLocaleTimeString(undefined, {
                                        hour: 'numeric',
                                        minute: '2-digit',
                                    })}
                                </p>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {groups.yesterday.length > 0 && (
                <div>
                    <p className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Yesterday</p>
                    <div className="space-y-1 px-2">
                        {groups.yesterday.map((conv) => (
                            <button
                                key={conv.session_id}
                                onClick={() => onSelect(conv.session_id)}
                                className={`w-full rounded px-2 py-2 text-left text-sm transition-colors ${activeSessionId === conv.session_id
                                        ? 'bg-blue-600 text-white'
                                        : 'text-gray-300 hover:bg-gray-800'
                                    }`}
                            >
                                <p className="truncate">{getConversationTitle(conv)}</p>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {groups.older.length > 0 && (
                <div>
                    <p className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Older</p>
                    <div className="space-y-1 px-2">
                        {groups.older.map((conv) => (
                            <button
                                key={conv.session_id}
                                onClick={() => onSelect(conv.session_id)}
                                className={`w-full rounded px-2 py-2 text-left text-sm transition-colors ${activeSessionId === conv.session_id
                                        ? 'bg-blue-600 text-white'
                                        : 'text-gray-300 hover:bg-gray-800'
                                    }`}
                            >
                                <p className="truncate">{getConversationTitle(conv)}</p>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
