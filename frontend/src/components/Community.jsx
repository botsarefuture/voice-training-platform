import React, { useEffect, useState } from 'react'

export default function Community({ apiBase, userId }) {
  const [posts, setPosts] = useState([])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')

  const loadPosts = () => {
    fetch(`${apiBase}/api/community`).then((r) => r.json()).then(setPosts)
  }

  useEffect(() => {
    loadPosts()
  }, [apiBase])

  const submit = async () => {
    if (!userId) return alert('Create a profile first')
    await fetch(`${apiBase}/api/community`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, title, body, is_anonymous: true }),
    })
    setTitle('')
    setBody('')
    loadPosts()
  }

  return (
    <section className="card">
      <h2>Community Sharing</h2>
      <p className="helper">Share wins, questions, or practice tips. Keep it supportive and safety‑focused.</p>
      <div className="panel">
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <textarea placeholder="Share a win or ask for feedback" value={body} onChange={(e) => setBody(e.target.value)} />
        <button onClick={submit}>Post</button>
      </div>
      <div className="progress-list">
        {posts.map((p) => (
          <div key={p.id} className="panel">
            <strong>{p.title}</strong>
            <p>{p.body}</p>
            <small>{new Date(p.created_at).toLocaleString()}</small>
          </div>
        ))}
      </div>
    </section>
  )
}
