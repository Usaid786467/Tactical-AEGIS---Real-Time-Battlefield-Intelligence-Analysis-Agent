/**
 * Tactical Map Component
 * Interactive map displaying threats and friendly forces in real-time
 */

import { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { useThreatData, useTrackingData, useWebSocket } from '@/hooks'
import { Threat, FriendlyForce } from '@/types'
import { Layers, MapPin, AlertTriangle, Shield } from 'lucide-react'

// Mapbox access token (should be in .env)
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || ''

interface TacticalMapProps {
  height?: string
  initialCenter?: [number, number]
  initialZoom?: number
}

function TacticalMap({
  height = '600px',
  initialCenter = [0, 0],
  initialZoom = 2,
}: TacticalMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const threatsMarkersRef = useRef<Map<number, mapboxgl.Marker>>(new Map())
  const unitsMarkersRef = useRef<Map<string, mapboxgl.Marker>>(new Map())

  const { threats } = useThreatData()
  const { units } = useTrackingData()
  const { isConnected } = useWebSocket({ channel: 'tactical' })

  const [showThreats, setShowThreats] = useState(true)
  const [showUnits, setShowUnits] = useState(true)
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null)
  const [selectedUnit, setSelectedUnit] = useState<FriendlyForce | null>(null)

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return

    // Initialize Mapbox
    if (MAPBOX_TOKEN) {
      mapboxgl.accessToken = MAPBOX_TOKEN
    }

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: initialCenter,
      zoom: initialZoom,
      attributionControl: false,
    })

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')

    // Add scale control
    map.current.addControl(
      new mapboxgl.ScaleControl({ unit: 'metric' }),
      'bottom-right'
    )

    return () => {
      map.current?.remove()
      map.current = null
    }
  }, [])

  // Update threat markers
  useEffect(() => {
    if (!map.current || !showThreats) {
      // Remove all threat markers if layer is hidden
      threatsMarkersRef.current.forEach((marker) => marker.remove())
      threatsMarkersRef.current.clear()
      return
    }

    const currentThreatIds = new Set(threats.map((t) => t.id))

    // Remove markers for threats that no longer exist
    threatsMarkersRef.current.forEach((marker, id) => {
      if (!currentThreatIds.has(id)) {
        marker.remove()
        threatsMarkersRef.current.delete(id)
      }
    })

    // Add or update markers for each threat
    threats.forEach((threat) => {
      let marker = threatsMarkersRef.current.get(threat.id)

      if (!marker) {
        // Create new marker
        const el = createThreatMarkerElement(threat)
        marker = new mapboxgl.Marker({ element: el, anchor: 'bottom' })
          .setLngLat([threat.longitude, threat.latitude])
          .addTo(map.current!)

        // Add click handler
        el.addEventListener('click', () => {
          setSelectedThreat(threat)
          setSelectedUnit(null)
        })

        threatsMarkersRef.current.set(threat.id, marker)
      } else {
        // Update existing marker position
        marker.setLngLat([threat.longitude, threat.latitude])
      }

      // Add popup
      const popup = new mapboxgl.Popup({ offset: 25, closeButton: true })
        .setHTML(createThreatPopupHTML(threat))

      marker.setPopup(popup)
    })
  }, [threats, showThreats])

  // Update unit markers
  useEffect(() => {
    if (!map.current || !showUnits) {
      // Remove all unit markers if layer is hidden
      unitsMarkersRef.current.forEach((marker) => marker.remove())
      unitsMarkersRef.current.clear()
      return
    }

    const currentUnitIds = new Set(units.map((u) => u.unit_id))

    // Remove markers for units that no longer exist
    unitsMarkersRef.current.forEach((marker, id) => {
      if (!currentUnitIds.has(id)) {
        marker.remove()
        unitsMarkersRef.current.delete(id)
      }
    })

    // Add or update markers for each unit
    units.forEach((unit) => {
      let marker = unitsMarkersRef.current.get(unit.unit_id)

      if (!marker) {
        // Create new marker
        const el = createUnitMarkerElement(unit)
        marker = new mapboxgl.Marker({ element: el, anchor: 'bottom' })
          .setLngLat([unit.longitude, unit.latitude])
          .addTo(map.current!)

        // Add click handler
        el.addEventListener('click', () => {
          setSelectedUnit(unit)
          setSelectedThreat(null)
        })

        unitsMarkersRef.current.set(unit.unit_id, marker)
      } else {
        // Update existing marker position
        marker.setLngLat([unit.longitude, unit.latitude])
      }

      // Add popup
      const popup = new mapboxgl.Popup({ offset: 25, closeButton: true })
        .setHTML(createUnitPopupHTML(unit))

      marker.setPopup(popup)
    })
  }, [units, showUnits])

  return (
    <div className="relative w-full" style={{ height }}>
      {/* Map Container */}
      <div ref={mapContainer} className="absolute inset-0 rounded-lg overflow-hidden" />

      {/* Layer Controls */}
      <div className="absolute top-4 left-4 bg-tactical-surface border border-tactical-border rounded-lg shadow-lg p-3 space-y-2">
        <div className="flex items-center justify-between mb-2 pb-2 border-b border-tactical-border">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-tactical-primary" />
            <span className="text-sm font-semibold text-tactical-primary uppercase">
              Layers
            </span>
          </div>
        </div>

        {/* Threats Layer Toggle */}
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showThreats}
            onChange={(e) => setShowThreats(e.target.checked)}
            className="form-checkbox h-4 w-4 text-threat-high bg-tactical-bg border-tactical-border rounded focus:ring-threat-high"
          />
          <AlertTriangle className="w-4 h-4 text-threat-high" />
          <span className="text-sm text-tactical-text">
            Threats ({threats.length})
          </span>
        </label>

        {/* Units Layer Toggle */}
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showUnits}
            onChange={(e) => setShowUnits(e.target.checked)}
            className="form-checkbox h-4 w-4 text-status-green bg-tactical-bg border-tactical-border rounded focus:ring-status-green"
          />
          <Shield className="w-4 h-4 text-status-green" />
          <span className="text-sm text-tactical-text">
            Friendly Forces ({units.length})
          </span>
        </label>
      </div>

      {/* Connection Status */}
      <div className="absolute top-4 right-4 bg-tactical-surface border border-tactical-border rounded-lg shadow-lg px-3 py-2">
        <div className="flex items-center space-x-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-status-green animate-pulse' : 'bg-status-red'
            }`}
          />
          <span className="text-xs text-tactical-muted font-mono">
            {isConnected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>
      </div>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 bg-tactical-surface border border-tactical-border rounded-lg shadow-lg p-3">
        <div className="flex items-center space-x-2 mb-2">
          <MapPin className="w-4 h-4 text-tactical-primary" />
          <span className="text-xs font-semibold text-tactical-primary uppercase">
            Legend
          </span>
        </div>
        <div className="space-y-1 text-xs text-tactical-text">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-threat-critical" />
            <span>Critical Threat</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-threat-high" />
            <span>High Threat</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-threat-medium" />
            <span>Medium Threat</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-threat-low" />
            <span>Low Threat</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-status-green" />
            <span>Friendly Unit (Green)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-status-amber" />
            <span>Friendly Unit (Amber)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-status-red" />
            <span>Friendly Unit (Red)</span>
          </div>
        </div>
      </div>

      {/* Selected Item Info */}
      {(selectedThreat || selectedUnit) && (
        <div className="absolute bottom-4 right-4 bg-tactical-surface border border-tactical-border rounded-lg shadow-lg p-4 max-w-sm">
          <button
            onClick={() => {
              setSelectedThreat(null)
              setSelectedUnit(null)
            }}
            className="absolute top-2 right-2 text-tactical-muted hover:text-tactical-text"
          >
            ×
          </button>
          {selectedThreat && <ThreatDetails threat={selectedThreat} />}
          {selectedUnit && <UnitDetails unit={selectedUnit} />}
        </div>
      )}
    </div>
  )
}

// Helper: Create threat marker element
function createThreatMarkerElement(threat: Threat): HTMLDivElement {
  const el = document.createElement('div')
  el.className = 'threat-marker'

  const colors = {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
    critical: '#dc2626',
  }

  const color = colors[threat.threat_level] || colors.medium

  el.innerHTML = `
    <div style="
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: ${color};
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      color: white;
      font-weight: bold;
      transition: transform 0.2s;
    " onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">
      !
    </div>
  `

  return el
}

// Helper: Create unit marker element
function createUnitMarkerElement(unit: FriendlyForce): HTMLDivElement {
  const el = document.createElement('div')
  el.className = 'unit-marker'

  const colors = {
    green: '#10b981',
    amber: '#f59e0b',
    red: '#ef4444',
    black: '#000000',
  }

  const color = colors[unit.status as keyof typeof colors] || colors.green

  el.innerHTML = `
    <div style="
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: ${color};
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      color: white;
      font-weight: bold;
      transition: transform 0.2s;
    " onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">
      ★
    </div>
  `

  return el
}

// Helper: Create threat popup HTML
function createThreatPopupHTML(threat: Threat): string {
  return `
    <div style="font-family: monospace; min-width: 200px;">
      <div style="font-weight: bold; color: #22c55e; margin-bottom: 8px; text-transform: uppercase;">
        Threat Detected
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Type:</strong> ${threat.threat_type}
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Level:</strong> <span style="color: ${getThreatColor(threat.threat_level)}; text-transform: uppercase;">${threat.threat_level}</span>
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Confidence:</strong> ${(threat.confidence * 100).toFixed(1)}%
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Detected:</strong> ${new Date(threat.detected_at).toLocaleString()}
      </div>
      ${threat.description ? `<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #ccc;">${threat.description}</div>` : ''}
    </div>
  `
}

// Helper: Create unit popup HTML
function createUnitPopupHTML(unit: FriendlyForce): string {
  return `
    <div style="font-family: monospace; min-width: 200px;">
      <div style="font-weight: bold; color: #22c55e; margin-bottom: 8px; text-transform: uppercase;">
        Friendly Force
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Unit ID:</strong> ${unit.unit_id}
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Name:</strong> ${unit.unit_name}
      </div>
      ${unit.callsign ? `<div style="margin-bottom: 4px;"><strong>Callsign:</strong> ${unit.callsign}</div>` : ''}
      <div style="margin-bottom: 4px;">
        <strong>Type:</strong> ${unit.unit_type}
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Status:</strong> <span style="color: ${getUnitStatusColor(unit.status)}; text-transform: uppercase;">${unit.status}</span>
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Personnel:</strong> ${unit.personnel_count}
      </div>
      <div style="margin-bottom: 4px;">
        <strong>Last Contact:</strong> ${new Date(unit.last_contact).toLocaleString()}
      </div>
    </div>
  `
}

// Helper: Get threat level color
function getThreatColor(level: string): string {
  const colors: Record<string, string> = {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
    critical: '#dc2626',
  }
  return colors[level] || colors.medium
}

// Helper: Get unit status color
function getUnitStatusColor(status: string): string {
  const colors: Record<string, string> = {
    green: '#10b981',
    amber: '#f59e0b',
    red: '#ef4444',
    black: '#000000',
  }
  return colors[status] || colors.green
}

// Threat details component
function ThreatDetails({ threat }: { threat: Threat }) {
  return (
    <div>
      <h3 className="text-sm font-bold text-threat-high uppercase mb-2">
        Threat Details
      </h3>
      <div className="space-y-1 text-xs text-tactical-text">
        <div>
          <span className="text-tactical-muted">ID:</span> {threat.id}
        </div>
        <div>
          <span className="text-tactical-muted">Type:</span> {threat.threat_type}
        </div>
        <div>
          <span className="text-tactical-muted">Level:</span>{' '}
          <span className={`font-bold text-threat-${threat.threat_level}`}>
            {threat.threat_level.toUpperCase()}
          </span>
        </div>
        <div>
          <span className="text-tactical-muted">Confidence:</span>{' '}
          {(threat.confidence * 100).toFixed(1)}%
        </div>
        <div>
          <span className="text-tactical-muted">Position:</span> {threat.latitude.toFixed(5)},{' '}
          {threat.longitude.toFixed(5)}
        </div>
        <div>
          <span className="text-tactical-muted">Source:</span> {threat.source}
        </div>
        <div>
          <span className="text-tactical-muted">Detected:</span>{' '}
          {new Date(threat.detected_at).toLocaleString()}
        </div>
        {threat.description && (
          <div className="mt-2 pt-2 border-t border-tactical-border">
            <span className="text-tactical-muted">Description:</span>
            <p className="mt-1">{threat.description}</p>
          </div>
        )}
      </div>
    </div>
  )
}

// Unit details component
function UnitDetails({ unit }: { unit: FriendlyForce }) {
  return (
    <div>
      <h3 className="text-sm font-bold text-status-green uppercase mb-2">
        Unit Details
      </h3>
      <div className="space-y-1 text-xs text-tactical-text">
        <div>
          <span className="text-tactical-muted">Unit ID:</span> {unit.unit_id}
        </div>
        <div>
          <span className="text-tactical-muted">Name:</span> {unit.unit_name}
        </div>
        {unit.callsign && (
          <div>
            <span className="text-tactical-muted">Callsign:</span> {unit.callsign}
          </div>
        )}
        <div>
          <span className="text-tactical-muted">Type:</span> {unit.unit_type}
        </div>
        <div>
          <span className="text-tactical-muted">Status:</span>{' '}
          <span className={`font-bold text-status-${unit.status}`}>
            {unit.status.toUpperCase()}
          </span>
        </div>
        <div>
          <span className="text-tactical-muted">Personnel:</span> {unit.personnel_count}
        </div>
        <div>
          <span className="text-tactical-muted">Position:</span> {unit.latitude.toFixed(5)},{' '}
          {unit.longitude.toFixed(5)}
        </div>
        <div>
          <span className="text-tactical-muted">Last Contact:</span>{' '}
          {new Date(unit.last_contact).toLocaleString()}
        </div>
        {unit.mission && (
          <div className="mt-2 pt-2 border-t border-tactical-border">
            <span className="text-tactical-muted">Mission:</span>
            <p className="mt-1">{unit.mission}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default TacticalMap
