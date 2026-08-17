import ConversationList from './ConversationList'

export default function ConversationSidebar({
    sessionId,
    messageCount,
    onNewChat,
    isOpen,
    onClose,
    disabled,
    conversations,
    onSelectConversation,
    loadingConversations,
    conversationError,
}) {
    const shortSession = sessionId ? `${sessionId.slice(0, 8)}...` : 'No session yet'

    const content = (
        <div className="flex h-full flex-col bg-gray-950 text-white">
            <div className="flex h-16 items-center justify-between border-b border-gray-800 px-4">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-300">Conversations</h2>
                <button
                    type="button"
                    onClick={onClose}
                    className="rounded px-2 py-1 text-sm text-gray-300 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400 md:hidden"
                >
                    Close
                </button>
            </div>

            <div className="flex-1 overflow-y-auto">
                <div className="p-4">
                    <button
                        type="button"
                        onClick={onNewChat}
                        disabled={disabled}
                        className="mb-4 w-full rounded border border-gray-700 px-3 py-2 text-left text-sm font-medium text-white hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        + New Chat
                    </button>

                    <div className="rounded border border-gray-800 bg-gray-900 p-3">
                        <p className="text-sm font-medium text-white">Current chat</p>
                        <p className="mt-1 text-xs text-gray-400">Session: {shortSession}</p>
                        <p className="mt-1 text-xs text-gray-400">{messageCount} message{messageCount === 1 ? '' : 's'}</p>
                    </div>
                </div>

                <ConversationList
                    conversations={conversations}
                    activeSessionId={sessionId}
                    onSelect={onSelectConversation}
                    loading={loadingConversations}
                    error={conversationError}
                />
            </div>
        </div>
    )

    return (
        <>
            <aside className="hidden w-72 shrink-0 border-r border-gray-200 md:block">
                {content}
            </aside>

            {isOpen && (
                <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true" aria-label="Conversations">
                    <button
                        type="button"
                        className="absolute inset-0 bg-gray-950/50"
                        onClick={onClose}
                        aria-label="Close conversations"
                    />
                    <div className="relative h-full w-80 max-w-[86vw] shadow-xl">
                        {content}
                    </div>
                </div>
            )}
        </>
    )
}
