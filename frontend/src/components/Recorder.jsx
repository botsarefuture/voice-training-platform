import React, { useEffect, useRef, useState } from 'react'

export default function Recorder({ apiBase, userId }) {
  const [recording, setRecording] = useState(false)
  const [chunks, setChunks] = useState([])
  const [transcription, setTranscription] = useState('')
  const [metrics, setMetrics] = useState(null)
  const [livePitch, setLivePitch] = useState(null)
  const [liveTip, setLiveTip] = useState('')
  const mediaRecorderRef = useRef(null)
  const analyserRef = useRef(null)
  const audioContextRef = useRef(null)
  const rafRef = useRef(null)
  const spectrogramRef = useRef(null)
  const pitchRef = useRef(null)

  useEffect(() => () => stopLiveAnalysis(), [])

  const startLiveAnalysis = async (stream) => {
    const AudioContext = window.AudioContext || window.webkitAudioContext
    audioContextRef.current = new AudioContext()
    const source = audioContextRef.current.createMediaStreamSource(stream)
    analyserRef.current = audioContextRef.current.createAnalyser()
    analyserRef.current.fftSize = 4096
    analyserRef.current.smoothingTimeConstant = 0.85
    source.connect(analyserRef.current)
    const buffer = new Float32Array(analyserRef.current.fftSize)
    const freqData = new Uint8Array(analyserRef.current.frequencyBinCount)

    const update = () => {
      analyserRef.current.getFloatTimeDomainData(buffer)
      analyserRef.current.getByteFrequencyData(freqData)
      const pitch = detectPitch(buffer, audioContextRef.current.sampleRate)
      if (pitch) {
        const smoothed = smoothPitch(pitchRef.current, pitch)
        pitchRef.current = smoothed
        const rounded = smoothed.toFixed(1)
        setLivePitch(rounded)
        setLiveTip(getPitchTip(smoothed))
      }
      drawSpectrogram(freqData, spectrogramRef.current)
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
      <div className="live-grid">
        <div>
          <p>Real-time pitch estimate: <strong>{livePitch ? `${livePitch} Hz` : '—'}</strong></p>
          <div className="pitch-visual">
            <div className="pitch-band lower">Lower &lt;155</div>
            <div className="pitch-band neutral">Neutral 155–185</div>
            <div className="pitch-band feminine">Feminine 185–300</div>
            <div className="pitch-band high">High &gt;300</div>
            <div className="pitch-marker" style={{ left: getPitchMarkerLeft(livePitch) }} />
          </div>
          <p className="helper">Target bands: neutral ~155–185 Hz • feminine ~185–300 Hz</p>
          <p className="tip">{liveTip || 'Tip: use relaxed airflow and gentle resonance. Avoid strain.'}</p>
        </div>
        <div>
          <p className="helper">Live spectrogram</p>
          <canvas ref={spectrogramRef} width={360} height={120} className="spectrogram" />
        </div>
      </div>
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
          {metrics.analysis_error && (
            <p className="helper">Analysis note: {metrics.analysis_error}. Try a longer recording or different browser.</p>
          )}
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
  const rms = Math.sqrt(buffer.reduce((sum, v) => sum + v * v, 0) / SIZE)
  if (rms < 0.01) return null

  // Apply a Hann window to reduce spectral leakage
  const windowed = new Float32Array(SIZE)
  for (let i = 0; i < SIZE; i++) {
    const w = 0.5 * (1 - Math.cos((2 * Math.PI * i) / (SIZE - 1)))
    windowed[i] = buffer[i] * w
  }

  const fmin = 80
  const fmax = 350
  const minLag = Math.floor(sampleRate / fmax)
  const maxLag = Math.floor(sampleRate / fmin)

  let bestLag = -1
  let bestCorr = 0

  for (let lag = minLag; lag <= maxLag; lag++) {
    let corr = 0
    for (let i = 0; i < SIZE - lag; i++) {
      corr += windowed[i] * windowed[i + lag]
    }
    corr /= (SIZE - lag)
    if (corr > bestCorr) {
      bestCorr = corr
      bestLag = lag
    }
  }

  if (bestCorr < 0.02 || bestLag === -1) return null

  // Parabolic interpolation for better accuracy
  const lag0 = Math.max(minLag, bestLag - 1)
  const lag1 = bestLag
  const lag2 = Math.min(maxLag, bestLag + 1)

  const c0 = autocorr(windowed, lag0)
  const c1 = autocorr(windowed, lag1)
  const c2 = autocorr(windowed, lag2)

  const denom = (2 * c1 - c2 - c0)
  const shift = denom !== 0 ? (c2 - c0) / (2 * denom) : 0
  const refinedLag = bestLag + shift

  return sampleRate / refinedLag
}

function autocorr(buffer, lag) {
  let corr = 0
  for (let i = 0; i < buffer.length - lag; i++) {
    corr += buffer[i] * buffer[i + lag]
  }
  return corr / (buffer.length - lag)
}

function smoothPitch(previous, current) {
  if (!previous) return current
  const alpha = 0.2
  return previous + alpha * (current - previous)
}

function drawSpectrogram(freqData, canvas) {
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const { width, height } = canvas
  const imageData = ctx.getImageData(1, 0, width - 1, height)
  ctx.putImageData(imageData, 0, 0)

  for (let y = 0; y < height; y++) {
    const freqIndex = Math.floor((y / height) * freqData.length)
    const value = freqData[freqIndex]
    const intensity = value / 255
    const color = `rgb(${Math.floor(30 + 180 * intensity)}, ${Math.floor(30 + 80 * intensity)}, ${Math.floor(60 + 140 * intensity)})`
    ctx.fillStyle = color
    ctx.fillRect(width - 1, height - y, 1, 1)
  }
}

function getPitchTip(pitch) {
  if (pitch < 155) {
    return 'Tip: try a gentle upward glide and keep airflow relaxed to raise pitch.'
  }
  if (pitch >= 155 && pitch <= 185) {
    return 'Tip: nice neutral range—add light resonance and melodic intonation.'
  }
  if (pitch > 185 && pitch <= 300) {
    return 'Tip: in a feminine band—maintain relaxed jaw and forward resonance.'
  }
  return 'Tip: high pitch detected—ease back to a comfortable, sustainable range.'
}

function getPitchMarkerLeft(livePitch) {
  if (!livePitch) return '0%'
  const pitch = Math.max(80, Math.min(350, parseFloat(livePitch)))
  const min = 80
  const max = 350
  const pct = ((pitch - min) / (max - min)) * 100
  return `${pct}%`
}
