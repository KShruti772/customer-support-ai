import { useContext, useEffect } from 'react'
import { useRouter } from 'next/router'
import { AuthContext } from '../pages/_app'

/**
 * Higher-Order Component (HOC) for protecting routes that require authentication.
 * 
 * Usage:
 *   export default withAuth(YourComponent)
 * 
 * Behavior:
 * 1. On mount, checks if app initialization is complete (auth state restored from localStorage)
 * 2. If not initialized, shows loading state (prevents redirect flicker)
 * 3. If initialized and no token, redirects to /login
 * 4. If initialized and has token, renders component
 * 5. If token is cleared (logout), redirects to /login
 */
export default function withAuth(Component) {
    return function ProtectedRoute(props) {
        const { token, isInitialized } = useContext(AuthContext)
        const router = useRouter()

        useEffect(() => {
            // Wait for auth state to be restored from localStorage
            if (!isInitialized || !router.isReady) {
                return
            }

            // Auth state is ready; unauthenticated users never see protected content.
            if (!token) {
                router.replace('/login')
            }
        }, [token, isInitialized, router])

        // Show nothing while:
        // - App is initializing auth state from localStorage
        // - Redirecting to /login (prevent flicker)
        if (!isInitialized || !token) {
            return null
        }

        // Render protected component
        return <Component {...props} />
    }
}
