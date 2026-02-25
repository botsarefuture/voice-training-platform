import React, { useEffect, useRef, useState } from 'react'

export default function Recorder({ apiBase, userId }) {
  const [recording, setRecording] = useState(false)
  const [chunks, setChunks] = useState([])
  const [transcription, setTranscription] = useState('')
  const [metrics, setMetrics] = useState(null)
  const [livePitch, setLivePitch] = useState(null)
  const mediaRecorderRef = useRef(null)
  const analyserRef = useRef(null)
  const audioContextRef = useRef(null)
  const rafRef = useRef(null)

  useEffect(() => () => stopLiveAnalysis(), [])

  const startLiveAnalysis = async (stream) => {
    const AudioContext = window.AudioContext || window.webkitAudioContext
    audioContextRef.current = new AudioContext()
    const source = audioContextRef.current.createMediaStreamSource(stream)
    analyserRef.current = audioContextRef.current.createAnalyser()
    analyserRef.current.fftSize = 2048
    source.connect(analyserRef.current)
    const buffer = new Float32Array(analyserRef.current.fftSize)

    const update = () => {
      analyserRef.current.getFloatTimeDomainData(buffer)
      const pitch = detectPitch(buffer, audioContextRef.current.sampleRate)
      if (pitch) setLivePitch(pitch.toFixed(1))
      rafRef.current = requestAnimationFrame(update)
    }
    update()
  }

  const stopLiveAnalysis = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    if (audioContextRef.current) audioContextRef.current.close()
    rafRef.current = null
    analyserRef.current = null
    audioContextRef.current = null
  }

  const startRecording = async () => {
    if (!userId) return alert('Create a profile first')
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    await startLiveAnalysis(stream)
    const mediaRecorder = new MediaRecorder(stream)
    mediaRecorderRef.current = mediaRecorder
    mediaRecorder.ondataavailable = (e) => setChunks((prev) => [...prev, e.data])
    mediaRecorder.onstop = async () => {
      stopLiveAnalysis()
      const blob = new Blob(chunks, { type: 'audio/webm' })
      setChunks([])
      await upload(blob)
    }
    mediaRecorder.start()
    setRecording(true)
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    setRecording(false)
  }

  const upload = async (blob) => {
    const form = new FormData()
    form.append('user_id', userId)
    form.append('audio', blob, 'recording.webm')
    const res = await fetch(`${apiBase}/api/audio/upload`, { method: 'POST', body: form })
    const data = await res.json()
    setTranscription(data.transcription || '')
    setMetrics(data.metrics || null)
  }

  return (
    <section className="card">
      <h2>Live Recording & Feedback</h2>
      <p>Real-time pitch estimate: <strong>{livePitch ? `${livePitch} Hz` : '—'}</strong></p>
      <p className="helper">Short, frequent sessions are safer. If you feel strain or hoarseness, stop and rest.</p>
      {!recording ? (
        <button onClick={startRecording}>Start Recording</button>
      ) : (
        <button onClick={stopRecording}>Stop Recording</button>
      )}

      {transcription && (
        <div className="panel">
          <h3>Transcription</h3>
          <p>{transcription}</p>
        </div>
      )}

      {metrics && (
        <div className="panel">
          <h3>Multi‑Dimensional Metrics</h3>
          <ul>
            <li>Average F0: {metrics.f0_mean?.toFixed(1)} Hz</li>
            <li>Median F0: {metrics.f0_median?.toFixed(1)} Hz</li>
            <li>Range: {metrics.f0_range?.toFixed(1)} Hz</li>
            <li>Pitch variability (std): {metrics.f0_std?.toFixed(1)} Hz</li>
            <li>Pitch band: {metrics.pitch_band || '—'} (neutral ~155–185 Hz)</li>
            <li>RMS (loudness proxy): {metrics.rms_mean?.toFixed(3)}</li>
            <li>Spectral Centroid (brightness proxy): {metrics.spectral_centroid_mean?.toFixed(1)}</li>
          </ul>
          <p className="helper">Pitch alone isn’t everything—resonance, intonation, and communication style matter.</p>
        </div>
      )}
    </section>
  )
}

function detectPitch(buffer, sampleRate) {
  const SIZE = buffer.length
  let bestOffset = -1
  let bestCorrelation = 0
  const rms = Math.sqrt(buffer.reduce((sum, v) => sum + v * v, 0) / SIZE)
  if (rms < 0.01) return null

  for (let offset = 50; offset < 1000; offset++) {
    let correlation = 0
    for (let i = 0; i < SIZE - offset; i++) {
      correlation += buffer[i] * buffer[i + offset]
    }
    correlation = correlation / (SIZE - offset)
    if (correlation > bestCorrelation) {
      bestCorrelation = correlation
      bestOffset = offset
    }
  }

  if (bestCorrelation > 0.01 && bestOffset !== -1) {
    return sampleRate / bestOffset
  }
  return null
}
