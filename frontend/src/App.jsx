import { useState, useCallback } from 'react'
import { MapContainer, TileLayer, Marker, Polyline, useMapEvents } from 'react-leaflet'
import L from 'leaflet'

// Vite doesn't resolve Leaflet's default icon URLs automatically
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const API = 'http://localhost:8000'

const ATLANTA = [33.749, -84.388]

const styles = {
  root: {
    display: 'flex',
    height: '100vh',
    fontFamily: "'Segoe UI', sans-serif",
  },
  sidebar: {
    width: 280,
    flexShrink: 0,
    padding: 20,
    background: '#0f172a',
    color: '#e2e8f0',
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
    overflowY: 'auto',
  },
  title: {
    fontSize: 22,
    fontWeight: 700,
    color: '#f43f5e',
    letterSpacing: 1,
  },
  hint: {
    fontSize: 12,
    color: '#94a3b8',
    lineHeight: 1.5,
  },
  coordBox: {
    background: '#1e293b',
    borderRadius: 6,
    padding: '10px 12px',
    fontSize: 12,
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  coordLabel: { color: '#94a3b8' },
  coordValue: { color: '#e2e8f0', fontFamily: 'monospace' },
  toggle: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    cursor: 'pointer',
    fontSize: 14,
    userSelect: 'none',
  },
  checkbox: { width: 16, height: 16, cursor: 'pointer', accentColor: '#f43f5e' },
  button: (enabled) => ({
    padding: '11px 0',
    background: enabled ? '#f43f5e' : '#334155',
    color: enabled ? '#fff' : '#64748b',
    border: 'none',
    borderRadius: 8,
    cursor: enabled ? 'pointer' : 'default',
    fontWeight: 700,
    fontSize: 14,
    transition: 'background 0.2s',
  }),
  error: {
    background: '#450a0a',
    border: '1px solid #f87171',
    borderRadius: 6,
    padding: '8px 10px',
    fontSize: 12,
    color: '#fca5a5',
  },
  divider: { borderTop: '1px solid #1e293b', margin: '2px 0' },
  routeCard: (color) => ({
    background: '#1e293b',
    borderRadius: 8,
    padding: '12px 14px',
    borderLeft: `4px solid ${color}`,
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  }),
  routeLabel: (color) => ({ fontWeight: 700, color, fontSize: 13 }),
  routeStat: { fontSize: 13, color: '#cbd5e1', display: 'flex', justifyContent: 'space-between' },
  statValue: { color: '#e2e8f0', fontWeight: 600 },
  resetBtn: {
    padding: '8px 0',
    background: 'transparent',
    color: '#64748b',
    border: '1px solid #334155',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 12,
    marginTop: 'auto',
  },
}

function ClickHandler({ onClick }) {
  useMapEvents({ click: (e) => onClick(e.latlng) })
  return null
}

function RouteCard({ label, color, route }) {
  return (
    <div style={styles.routeCard(color)}>
      <div style={styles.routeLabel(color)}>{label} Route</div>
      <div style={styles.routeStat}>
        <span>Travel time</span>
        <span style={styles.statValue}>{route.time_minutes} min</span>
      </div>
      <div style={styles.routeStat}>
        <span>Danger score</span>
        <span style={styles.statValue}>{route.danger_score}</span>
      </div>
    </div>
  )
}

export default function App() {
  const [points, setPoints] = useState([])   // [{lat, lng}, {lat, lng}]
  const [isRaining, setIsRaining] = useState(false)
  const [routes, setRoutes] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleMapClick = useCallback((latlng) => {
    setPoints((prev) => {
      if (prev.length >= 2) return [latlng]  // reset to new start on 3rd click
      return [...prev, latlng]
    })
    setRoutes(null)
    setError(null)
  }, [])

  const handleReset = () => {
    setPoints([])
    setRoutes(null)
    setError(null)
  }

  const calculateRoute = async () => {
    if (points.length < 2 || loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_lat: points[0].lat,
          start_lon: points[0].lng,
          end_lat: points[1].lat,
          end_lon: points[1].lng,
          isRaining,
        }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(body.detail || res.statusText)
      }
      setRoutes(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const canRoute = points.length === 2 && !loading

  return (
    <div style={styles.root}>
      <div style={styles.sidebar}>
        <div style={styles.title}>CRASHOUTS</div>
        <div style={styles.hint}>
          Click the map to place a start point, then an end point. A third click resets.
        </div>

        <div style={styles.coordBox}>
          <div style={styles.coordLabel}>Start</div>
          <div style={styles.coordValue}>
            {points[0] ? `${points[0].lat.toFixed(5)}, ${points[0].lng.toFixed(5)}` : '—'}
          </div>
          <div style={{ ...styles.coordLabel, marginTop: 6 }}>End</div>
          <div style={styles.coordValue}>
            {points[1] ? `${points[1].lat.toFixed(5)}, ${points[1].lng.toFixed(5)}` : '—'}
          </div>
        </div>

        <label style={styles.toggle}>
          <input
            type="checkbox"
            style={styles.checkbox}
            checked={isRaining}
            onChange={(e) => { setIsRaining(e.target.checked); setRoutes(null) }}
          />
          Raining conditions
        </label>

        <button style={styles.button(canRoute)} onClick={calculateRoute} disabled={!canRoute}>
          {loading ? 'Calculating…' : 'Calculate Routes'}
        </button>

        {error && <div style={styles.error}>{error}</div>}

        {routes && (
          <>
            <div style={styles.divider} />
            <RouteCard label="Baseline" color="#3b82f6" route={routes.baseline} />
            <RouteCard label="Safer" color="#22c55e" route={routes.safer} />
          </>
        )}

        <button style={styles.resetBtn} onClick={handleReset}>Clear map</button>
      </div>

      <MapContainer center={ATLANTA} zoom={13} style={{ flex: 1 }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ClickHandler onClick={handleMapClick} />

        {points[0] && <Marker position={points[0]} />}
        {points[1] && <Marker position={points[1]} />}

        {routes?.baseline?.coordinates?.length > 0 && (
          <Polyline positions={routes.baseline.coordinates} color="#3b82f6" weight={5} opacity={0.85} />
        )}
        {routes?.safer?.coordinates?.length > 0 && (
          <Polyline positions={routes.safer.coordinates} color="#22c55e" weight={5} opacity={0.85} />
        )}
      </MapContainer>
    </div>
  )
}
