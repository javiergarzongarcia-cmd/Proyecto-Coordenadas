import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import RouteList from './pages/RouteList'
import RouteCreate from './pages/RouteCreate'
import RouteDetail from './pages/RouteDetail'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RouteList />} />
        <Route path="/create" element={<RouteCreate />} />
        <Route path="/routes/:id" element={<RouteDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')).render(<App />)
