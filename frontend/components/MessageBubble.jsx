function formatTime(value) {
    if (!value) return ''
    return new Intl.DateTimeFormat(undefined, {
        hour: 'numeric',
        minute: '2-digit',
    }).format(value)
}

function sourceLabel(source, index) {
    if (!source || typeof source !== 'object') return `Source ${index + 1}`
    if (source.title) return source.title
    if (source.name) return source.name
    if (source.doc_id) return source.doc_id
    if (source.source_path) {
        const parts = String(source.source_path).split(/[\\/]/)
        return parts[parts.length - 1] || `Source ${index + 1}`
    }
    return `Source ${index + 1}`
}

function sourceSnippet(source) {
    if (!source || typeof source !== 'object') return ''
    return source.text || source.snippet || source.content || ''
}

export default function MessageBubble({ message }) {
    const isUser = message.role === 'user'
    const sources = Array.isArray(message.sources) ? message.sources : []

    return (
        <article className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[88%] sm:max-w-[78%] ${isUser ? 'items-end' : 'items-start'}`}>
                <div
                    className={`rounded-lg px-4 py-3 shadow-sm ${
                        isUser
                            ? 'bg-blue-700 text-white'
                            : 'border border-gray-200 bg-white text-gray-950'
                    }`}
                >
                    <p className="whitespace-pre-wrap break-words text-sm leading-6">{message.content}</p>
                </div>

                <div className={`mt-1 flex items-center gap-2 text-xs text-gray-500 ${isUser ? 'justify-end' : 'justify-start'}`}>
                    <span>{isUser ? 'You' : 'AI'}</span>
                    <span aria-hidden="true">&middot;</span>
                    <time dateTime={message.timestamp?.toISOString?.()}>{formatTime(message.timestamp)}</time>
                </div>

                {!isUser && message.escalate && (
                    <div className="mt-3 rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950" role="status">
                        This issue may require assistance from a human support representative.
                    </div>
                )}

                {!isUser && sources.length > 0 && (
                    <details className="mt-3 rounded border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700">
                        <summary className="cursor-pointer font-medium text-gray-800">Sources</summary>
                        <ul className="mt-2 space-y-2">
                            {sources.map((source, index) => {
                                const snippet = sourceSnippet(source)
                                return (
                                    <li key={`${sourceLabel(source, index)}-${index}`} className="border-t border-gray-200 pt-2 first:border-t-0 first:pt-0">
                                        <p className="font-medium text-gray-900">{sourceLabel(source, index)}</p>
                                        {snippet && <p className="mt-1 line-clamp-3 whitespace-pre-wrap break-words text-gray-600">{snippet}</p>}
                                    </li>
                                )
                            })}
                        </ul>
                    </details>
                )}
            </div>
        </article>
    )
}
