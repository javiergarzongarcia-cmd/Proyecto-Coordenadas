import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function RouteList() {
  const [routes, setRoutes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/api/routes`)
      .then(r => r.json())
      .then(setRoutes)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ padding: 16 }}>Cargando...</div>
  if (error) return <div style={{ padding: 16 }}>Error: {error}</div>

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 16 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Rutas</h1>
        <Link to="/create">Crear ruta</Link>
      </header>
      <table width="100%" cellPadding={8} style={{ borderCollapse: 'collapse', marginTop: 12 }}>
        <thead>
          <tr>
            <th align="left">Nombre</th>
            <th>Waypoints</th>
            <th>Distancia (km)</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {routes.map(r => (
            <tr key={r.id} style={{ borderTop: '1px solid #ddd' }}>
              <td>{r.name}</td>
              <td align="center">{r.waypoint_count ?? '-'}</td>
              <td align="right">{r.total_distance_km?.toFixed?.(3) ?? r.total_distance_km}</td>
              <td align="center">
                <Link to={`/routes/${r.id}`}>Ver</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
