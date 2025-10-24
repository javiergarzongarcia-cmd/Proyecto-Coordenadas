import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function RouteDetail() {
  const { id } = useParams()
  const [route, setRoute] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/api/routes/${id}`)
      .then(r => {
        if (!r.ok) throw new Error('No se encontró la ruta')
        return r.json()
      })
      .then(setRoute)
      .catch(e => setError(e.message))
  }, [id])

  if (error) return <div style={{ padding: 16 }}>Error: {error}</div>
  if (!route) return <div style={{ padding: 16 }}>Cargando...</div>

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 16 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>{route.name}</h1>
        <Link to="/">Volver</Link>
      </header>
      <div style={{ marginTop: 12 }}>
        <strong>Distancia total:</strong> {route.total_distance_km?.toFixed?.(3) ?? route.total_distance_km} km
      </div>
      <h3 style={{ marginTop: 12 }}>Waypoints</h3>
      <ol>
        {route.waypoints.map(w => (
          <li key={w.id}>
            {w.order}. lat: {w.latitude}, lng: {w.longitude}
          </li>
        ))}
      </ol>
    </div>
  )
}
