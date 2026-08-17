import '../styles/globals.css'
import { createContext, useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import * as api from '../lib/api'

export const AuthContext = createContext({})

function MyApp({ Component, pageProps }) {
    const [token, setToken] = useState(null)
    const [user, setUser] = useState(null)
    const [isInitialized, setIsInitialized] = useState(false)
    const router = useRouter()

    // Initialize authentication from localStorage
    // Must happen once on app startup
    useEffect(() => {
        const t = localStorage.getItem('auth_token')
        const u = localStorage.getItem('auth_user')
        if (t) {
            setToken(t)
            api.setAuthToken(t)
        }
        if (u) setUser(JSON.parse(u))
        // Mark initialization complete - unblock protected route redirects
        setIsInitialized(true)
    }, [])

    const login = (token, user) => {
        localStorage.setItem('auth_token', token)
        localStorage.setItem('auth_user', JSON.stringify(user))
        setToken(token)
        setUser(user)
    }

    const logout = () => {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        api.setAuthToken(null)
        setToken(null)
        setUser(null)
        router.push('/login')
    }

    return (
        <AuthContext.Provider value={{ token, user, login, logout, isInitialized }}>
            <div className="app-shell">
                <Component {...pageProps} />
            </div>
        </AuthContext.Provider>
    )
}

export default MyApp
