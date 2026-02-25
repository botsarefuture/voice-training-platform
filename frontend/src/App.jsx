import React, { useEffect, useState } from 'react'
import Recorder from './components/Recorder.jsx'
import Progress from './components/Progress.jsx'
import Modules from './components/Modules.jsx'
import Community from './components/Community.jsx'

const API_BASE = import.meta.env.VITE_API_BASE || ''

export default function App() {
  const [userId, setUserId] = useState(localStorage.getItem('userId') || '')

  useEffect(() => {
    if (!userId) return
    localStorage.setItem('userId', userId)
  }, [userId])

  const createUser = async () => {
    const res = await fetch(`${API_BASE}/api/users`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) })
    const data = await res.json()
    setUserId(data.id)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Voice Training Platform</h1>
        <p>Local-first voice training with live feedback and progress tracking</p>
      </header>

      <section className="card">
        <h2>Profile</h2>
        {userId ? (
          <p>Your local user id: <code>{userId}</code></p>
        ) : (
          <button onClick={createUser}>Create local profile</button>
        )}
      </section>

      <Recorder apiBase={API_BASE} userId={userId} />
      <Progress apiBase={API_BASE} userId={userId} />
      <Modules apiBase={API_BASE} />
      <Community apiBase={API_BASE} userId={userId} />
    </div>
  )
}
