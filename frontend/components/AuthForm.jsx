import { useState } from 'react'

export default function AuthForm({ mode = 'login', onSubmit, error }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [localError, setLocalError] = useState(null)
    const [loading, setLoading] = useState(false)

    const submit = async (e) => {
        e.preventDefault()
        setLocalError(null)

        // Client-side validation
        if (!username.trim()) {
            setLocalError('Username is required')
            return
        }
        if (!password) {
            setLocalError('Password is required')
            return
        }

        if (mode === 'register') {
            if (!confirmPassword) {
                setLocalError('Please confirm your password')
                return
            }
            if (password !== confirmPassword) {
                setLocalError('Passwords do not match')
                return
            }
        }

        setLoading(true)
        try {
            await onSubmit({ username, password })
            // Clear sensitive data after successful submission
            setPassword('')
            setConfirmPassword('')
        } catch (err) {
            // Keep password fields on error for retry
        } finally {
            setLoading(false)
        }
    }

    const displayError = error || localError

    return (
        <form onSubmit={submit} className="max-w-md bg-white shadow-md rounded p-6">
            <h2 className="text-2xl font-semibold mb-4">{mode === 'login' ? 'Sign in' : 'Create account'}</h2>
            {displayError && <div className="bg-red-50 text-red-800 p-3 rounded mb-4 text-sm">{displayError}</div>}

            <label className="block text-sm font-medium text-gray-700">Username</label>
            <input
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="mt-1 mb-3 block w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={loading}
                autoComplete="username"
            />

            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="mt-1 mb-3 block w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={loading}
                autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
            />

            {mode === 'register' && (
                <>
                    <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
                    <input
                        type="password"
                        value={confirmPassword}
                        onChange={e => setConfirmPassword(e.target.value)}
                        className="mt-1 mb-4 block w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        disabled={loading}
                        autoComplete="new-password"
                    />
                </>
            )}

            {mode !== 'register' && <div className="mb-4" />}

            <button
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
                {loading ? (mode === 'login' ? 'Signing in...' : 'Creating account...') : (mode === 'login' ? 'Sign in' : 'Create account')}
            </button>
        </form>
    )
}
