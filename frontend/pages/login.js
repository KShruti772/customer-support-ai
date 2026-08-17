import { useContext, useState } from 'react'
import { useRouter } from 'next/router'
import AuthForm from '../components/AuthForm'
import * as api from '../lib/api'
import { AuthContext } from './_app'

export default function LoginPage() {
    const { login } = useContext(AuthContext)
    const [error, setError] = useState(null)
    const router = useRouter()
    const isNewRegistration = router.query.registered === 'true'

    const handle = async ({ username, password }) => {
        setError(null)
        try {
            const data = await api.login(username, password)
            const token = data.access_token
            login(token, { username })
            api.setAuthToken && api.setAuthToken(token)
            router.push('/chat')
        } catch (e) {
            setError(e.response?.data?.detail || 'Login failed')
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="w-full max-w-2xl px-4">
                <div className="flex items-center justify-between mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Customer Support</h1>
                </div>

                {isNewRegistration && (
                    <div className="mb-4 p-4 bg-blue-50 text-blue-800 rounded border border-blue-200">
                        Registration successful! Please log in with your credentials.
                    </div>
                )}

                <AuthForm mode="login" onSubmit={handle} error={error} />
                <p className="mt-4 text-sm text-gray-600 text-center">Don't have an account? <a href="/register" className="text-blue-600 hover:text-blue-700 font-medium">Create one</a></p>
            </div>
        </div>
    )
}
