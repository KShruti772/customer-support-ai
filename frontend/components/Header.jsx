export default function Header({ user, onLogout, onOpenSidebar }) {
    return (
        <header className="border-b border-gray-200 bg-white">
            <div className="flex h-16 items-center justify-between px-4 sm:px-6">
                <div className="flex min-w-0 items-center gap-3">
                    <button
                        type="button"
                        onClick={onOpenSidebar}
                        className="rounded border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 md:hidden"
                        aria-label="Open conversations"
                    >
                        Conversations
                    </button>
                    <div className="min-w-0">
                        <h1 className="truncate text-lg font-semibold text-gray-950 sm:text-xl">Customer Support AI</h1>
                        {user?.username && (
                            <p className="truncate text-xs text-gray-500 sm:text-sm">Signed in as {user.username}</p>
                        )}
                    </div>
                </div>

                <button
                    type="button"
                    onClick={onLogout}
                    className="rounded border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    Logout
                </button>
            </div>
        </header>
    )
}
