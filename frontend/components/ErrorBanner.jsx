export default function ErrorBanner({ message, onDismiss }) {
    if (!message) return null

    return (
        <div
            role="alert"
            className="flex items-start justify-between gap-4 border-b border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900 sm:px-6"
        >
            <div>
                <p className="font-semibold">Something went wrong</p>
                <p>{message}</p>
            </div>
            {onDismiss && (
                <button
                    type="button"
                    onClick={onDismiss}
                    className="shrink-0 rounded px-2 py-1 text-sm font-medium text-red-900 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                    Dismiss
                </button>
            )}
        </div>
    )
}
