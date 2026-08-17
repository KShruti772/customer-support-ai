export default function LoadingIndicator() {
    return (
        <div className="flex items-center gap-2 text-sm text-gray-600" aria-live="polite">
            <span className="inline-flex h-2 w-2 rounded-full bg-blue-600" />
            <span>AI is preparing a response...</span>
        </div>
    )
}
