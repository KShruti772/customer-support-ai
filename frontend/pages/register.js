import { useContext, useState } from 'react'
import { useRouter } from 'next/router'
import AuthForm from '../components/AuthForm'
import * as api from '../lib/api'

export default function RegisterPage() {
    const [error, setError] = useState(null)
    const [success, setSuccess] = useState(false)
    const router = useRouter()

    const handleRegister = async ({ username, password }) => {
        setError(null)
        setSuccess(false)
        try {
            // Call backend registration endpoint
            const data = await api.register(username, password)

            // Registration successful - redirect to login with message
            setSuccess(true)
            setTimeout(() => {
                router.push('/login?registered=true')
            }, 1500)
        } catch (e) {
            // Handle various error responses
            if (e.response?.status === 400) {
                setError('Username already exists or invalid input')
            } else if (e.response?.status === 500) {
                setError('Server error. Please try again later.')
            } else if (e.message === 'Network Error') {
                setError('Network error. Please check your connection.')
            } else {
                setError(e.response?.data?.detail || 'Registration failed')
            }
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="w-full max-w-2xl px-4">
                <div className="flex items-center justify-between mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Customer Support</h1>
                </div>

                {success && (
                    <div className="mb-4 p-4 bg-green-50 text-green-800 rounded border border-green-200">
                        Account created successfully! Redirecting to login...
                    </div>
                )}

                <AuthForm mode="register" onSubmit={handleRegister} error={error} />

                <p className="mt-4 text-sm text-gray-600 text-center">
                    Already have an account? <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">Sign in</a>
                </p>
            </div>
        </div>
    )
}
