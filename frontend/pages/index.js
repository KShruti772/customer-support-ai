import { useEffect, useState } from 'react'

export default function Home() {
    const [health, setHealth] = useState(null)

    useEffect(() => {
        fetch('http://localhost:8000/health')
            .then(res => res.json())
            .then(data => setHealth(data))
            .catch(() => setHealth({ status: 'unreachable' }))
    }, [])

    return (
        <div style={{ fontFamily: 'system-ui, sans-serif', padding: 24 }}>
            <h1>Customer Support Assistant — Frontend</h1>
            <p>Backend health: {health ? health.status : 'loading...'}</p>
        </div>
    )
}
