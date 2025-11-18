/**
 * Map View Page
 * Full-screen tactical map with integrated controls
 */

import { useState } from 'react'
import TacticalMap from '@/components/TacticalMap'
import { useThreatData, useTrackingData } from '@/hooks'
import { Shield, AlertTriangle, Map, RefreshCw } from 'lucide-react'

function MapView() {
  const { threats, isLoading: threatsLoading, refetch: refetchThreats } = useThreatData()
  const { units, isLoading: unitsLoading, refetch: refetchUnits } = useTrackingData()

  const [mapCenter] = useState<[number, number]>([0, 0])
  const [mapZoom] = useState<number>(2)

  const handleRefresh = () => {
    refetchThreats()
    refetchUnits()
  }

  const criticalThreats = threats.filter((t) => t.threat_level === 'critical').length
  const highThreats = threats.filter((t) => t.threat_level === 'high').length
  const activeUnits = units.filter((u) => u.active).length

  return (
    <div className="h-full flex flex-col bg-tactical-bg">
      {/* Header */}
      <header className="bg-tactical-surface border-b border-tactical-border px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Map className="w-6 h-6 text-tactical-primary" />
            <div>
              <h1 className="text-xl font-bold text-tactical-primary font-mono">
                TACTICAL MAP
              </h1>
              <p className="text-xs text-tactical-muted">
                Real-Time Battlefield Visualization
              </p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-threat-high" />
              <div className="text-xs">
                <div className="text-tactical-muted">Threats</div>
                <div className="font-mono font-bold text-tactical-text">
                  {threats.length}{' '}
                  <span className="text-threat-critical">
                    ({criticalThreats} CRIT
                  </span>
                  ,{' '}
                  <span className="text-threat-high">
                    {highThreats} HIGH)
                  </span>
                </div>
              </div>
            </div>

            <div className="h-8 w-px bg-tactical-border" />

            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-status-green" />
              <div className="text-xs">
                <div className="text-tactical-muted">Forces</div>
                <div className="font-mono font-bold text-tactical-text">
                  {activeUnits} / {units.length} Active
                </div>
              </div>
            </div>

            <div className="h-8 w-px bg-tactical-border" />

            <button
              onClick={handleRefresh}
              disabled={threatsLoading || unitsLoading}
              className="btn-secondary flex items-center space-x-2 text-xs"
            >
              <RefreshCw
                className={`w-3 h-3 ${
                  threatsLoading || unitsLoading ? 'animate-spin' : ''
                }`}
              />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      {/* Map */}
      <main className="flex-1 p-4">
        <TacticalMap
          height="100%"
          initialCenter={mapCenter}
          initialZoom={mapZoom}
        />
      </main>
    </div>
  )
}

export default MapView
