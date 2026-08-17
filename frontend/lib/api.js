import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

const client = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
})

export function setAuthToken(token) {
    if (token) client.defaults.headers.common['Authorization'] = `Bearer ${token}`
    else delete client.defaults.headers.common['Authorization']
}

// Handle 401 responses by clearing invalid/expired tokens
client.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            // Clear invalid or expired token
            setAuthToken(null)
            localStorage.removeItem('auth_token')
            localStorage.removeItem('auth_user')
            // Redirect to login if not already there
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export async function register(username, password) {
    const r = await client.post('/auth/register', { username, password })
    return r.data
}

export async function login(username, password) {
    const r = await client.post('/auth/login', { username, password })
    return r.data
}

export async function createConversation(payload) {
    const r = await client.post('/conversations', payload)
    return r.data
}

export async function sendChat(message, session_id) {
    const payload = { message }
    if (session_id) payload.session_id = session_id
    const r = await client.post('/chat', payload)
    return r.data
}

export async function getConversationsForUser(user_id) {
    const r = await client.get(`/conversations/user/${user_id}`)
    return r.data
}

export async function getHistory(session_id, max_messages = 20) {
    const r = await client.get(`/conversations/${session_id}/history?max_messages=${max_messages}`)
    return r.data
}

export default client
