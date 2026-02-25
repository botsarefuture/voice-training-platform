import React, { useEffect, useState } from 'react'

export default function Modules({ apiBase }) {
  const [modules, setModules] = useState([])

  useEffect(() => {
    fetch(`${apiBase}/api/modules`).then((r) => r.json()).then(setModules)
  }, [apiBase])

  return (
    <section className="card">
      <h2>Training Modules</h2>
      <p className="helper">Based on UCSF guidance: focus on pitch, resonance, intonation, and communication habits.</p>
      {modules.length === 0 ? (
        <p>No modules yet. Seed from the backend to start guided exercises.</p>
      ) : (
        modules.map((m) => (
          <div key={m.id} className="panel">
            <h3>{m.title}</h3>
            <p>{m.description}</p>
            <ol>
              {m.steps?.map((step, idx) => <li key={idx}>{step}</li>)}
            </ol>
          </div>
        ))
      )}
    </section>
  )
}
