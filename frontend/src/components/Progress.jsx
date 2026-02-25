import React, { useEffect, useState } from 'react'

export default function Progress({ apiBase, userId }) {
  const [sessions, setSessions] = useState([])

  useEffect(() => {
    if (!userId) return
    fetch(`${apiBase}/api/progress/${userId}`).then((r) => r.json()).then((data) => {
      setSessions(data.sessions || [])
    })
  }, [apiBase, userId])

  return (
    <section className="card">
      <h2>Progress Dashboard</h2>
      {sessions.length === 0 ? (
        <p>No sessions yet. Record to start tracking progress.</p>
      ) : (
        <div className="progress-list">
          {sessions.map((s) => (
            <div key={s.session_id} className="panel">
              <strong>{new Date(s.created_at).toLocaleString()}</strong>
              <div>F0 Mean: {s.metrics.f0_mean?.toFixed(1)} Hz</div>
              <div>Range: {s.metrics.f0_range?.toFixed(1)} Hz</div>
              <div>Variability: {s.metrics.f0_std?.toFixed(1)} Hz</div>
              <div>Band: {s.metrics.pitch_band || '—'}</div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
