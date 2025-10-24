import React, { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371.0088
  const toRad = d => (d * Math.PI) / 180
  const dPhi = toRad(lat2 - lat1)
  const dLambda = toRad(lon2 - lon1)
  const a = Math.sin(dPhi / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLambda / 2) ** 2
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

export default function RouteCreate() {
  const [name, setName] = useState('')
  const [waypoints, setWaypoints] = useState([{ latitude: '', longitude: '', order: 1 }])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const navigate = useNavigate()

  const distanceKm = useMemo(() => {
    let total = 0
    const points = [...waypoints]
      .filter(w => w.latitude !== '' && w.longitude !== '')
      .sort((a, b) => a.order - b.order)
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1]
      const b = points[i]
      total += haversineKm(Number(a.latitude), Number(a.longitude), Number(b.latitude), Number(b.longitude))
    }
    return Math.round(total * 1000) / 1000
  }, [waypoints])

  function addWaypoint() {
    const nextOrder = (waypoints.at(-1)?.order ?? 0) + 1
    setWaypoints([...waypoints, { latitude: '', longitude: '', order: nextOrder }])
  }

  function removeWaypoint(idx) {
    setWaypoints(waypoints.filter((_, i) => i !== idx))
  }

  function updateWaypoint(idx, field, value) {
    setWaypoints(waypoints.map((w, i) => (i === idx ? { ...w, [field]: value } : w)))
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    if (!name.trim()) {
      setError('El nombre es obligatorio')
      return
    }
    const payload = {
      name,
      waypoints: waypoints
        .filter(w => w.latitude !== '' && w.longitude !== '')
        .map(w => ({ latitude: Number(w.latitude), longitude: Number(w.longitude), order: Number(w.order) })),
    }
    if (payload.waypoints.length === 0) {
      setError('Agregue al menos un waypoint')
      return
    }
    setSaving(true)
    try {
      const res = await fetch(`${API_BASE}/api/routes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      navigate(`/routes/${data.id}`)
    } catch (e) {
      setError(String(e))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 16 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Crear ruta</h1>
        <Link to="/">Volver</Link>
      </header>
      <form onSubmit={onSubmit} style={{ marginTop: 12 }}>
        <div style={{ marginBottom: 12 }}>
          <label>Nombre</label>
          <input value={name} onChange={e => setName(e.target.value)} required style={{ marginLeft: 8 }} />
        </div>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Waypoints</h3>
            <button type="button" onClick={addWaypoint}>+ Añadir</button>
          </div>
          {waypoints.map((w, i) => (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 100px 100px', gap: 8, marginBottom: 8 }}>
              <input type="number" step="0.000001" placeholder="Latitud (-90 a 90)" value={w.latitude} onChange={e => updateWaypoint(i, 'latitude', e.target.value)} required />
              <input type="number" step="0.000001" placeholder="Longitud (-180 a 180)" value={w.longitude} onChange={e => updateWaypoint(i, 'longitude', e.target.value)} required />
              <input type="number" min={1} placeholder="Orden" value={w.order} onChange={e => updateWaypoint(i, 'order', Number(e.target.value))} />
              <button type="button" onClick={() => removeWaypoint(i)}>- Eliminar</button>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 12 }}>
          <strong>Distancia calculada:</strong> {distanceKm.toFixed(3)} km
        </div>
        <div style={{ marginTop: 16 }}>
          <button type="submit" disabled={saving}>{saving ? 'Guardando...' : 'Guardar ruta'}</button>
        </div>
        {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
      </form>
    </div>
  )
}
