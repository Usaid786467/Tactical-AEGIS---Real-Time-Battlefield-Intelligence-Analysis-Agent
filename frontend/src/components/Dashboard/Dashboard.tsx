import { useState, useEffect } from 'react'
import { Shield, Radio, AlertTriangle, Map, Activity } from 'lucide-react'
import { useThreatData, useTrackingData, useWebSocket } from '@/hooks'
import { apiClient } from '@/services/api'

function Dashboard() {
  const { threats, isLoading: threatsLoading } = useThreatData()
  const { units, isLoading: unitsLoading } = useTrackingData()
  const { isConnected } = useWebSocket({ channel: 'tactical' })

  const [tacticalPicture, setTacticalPicture] = useState<any>(null)

  useEffect(() => {
    // Fetch tactical picture
    apiClient.getTacticalPicture().then(setTacticalPicture).catch(console.error)
  }, [])

  const criticalThreats = threats.filter((t) => t.threat_level === 'critical').length
  const highThreats = threats.filter((t) => t.threat_level === 'high').length
  const activeUnits = units.filter((u) => u.active).length
  const unitsAtRisk = tacticalPicture?.situation_assessment?.units_at_risk || 0

  return (
    <div className="h-full flex flex-col bg-tactical-bg">
      {/* Main Content */}
      <main className="flex-1 overflow-auto p-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Total Threats */}
          <StatCard
            icon={<AlertTriangle className="w-6 h-6" />}
            title="Total Threats"
            value={threats.length}
            subtitle={`${criticalThreats} Critical, ${highThreats} High`}
            color="red"
            loading={threatsLoading}
          />

          {/* Active Units */}
          <StatCard
            icon={<Map className="w-6 h-6" />}
            title="Active Units"
            value={activeUnits}
            subtitle={`${unitsAtRisk} at risk`}
            color="green"
            loading={unitsLoading}
          />

          {/* Situation Status */}
          <StatCard
            icon={<Activity className="w-6 h-6" />}
            title="Situation"
            value={tacticalPicture?.situation_assessment?.status?.toUpperCase() || 'LOADING'}
            subtitle={tacticalPicture?.situation_assessment?.summary || ''}
            color="amber"
            loading={!tacticalPicture}
          />

          {/* Real-Time Updates */}
          <StatCard
            icon={<Radio className="w-6 h-6" />}
            title="Real-Time"
            value={isConnected ? 'ACTIVE' : 'OFFLINE'}
            subtitle="WebSocket Connection"
            color={isConnected ? 'green' : 'red'}
            loading={false}
          />
        </div>

        {/* Panels Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Threats Panel */}
          <div className="panel">
            <div className="panel-header">
              <h2 className="panel-title">Recent Threats</h2>
              <span className="badge badge-critical">{threats.length} Active</span>
            </div>
            <div className="space-y-2 max-h-96 overflow-auto">
              {threatsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="spinner" />
                </div>
              ) : threats.length === 0 ? (
                <p className="text-tactical-muted text-center py-8">
                  No threats detected
                </p>
              ) : (
                threats.slice(0, 10).map((threat) => (
                  <ThreatItem key={threat.id} threat={threat} />
                ))
              )}
            </div>
          </div>

          {/* Units Panel */}
          <div className="panel">
            <div className="panel-header">
              <h2 className="panel-title">Friendly Forces</h2>
              <span className="badge badge-green">{activeUnits} Active</span>
            </div>
            <div className="space-y-2 max-h-96 overflow-auto">
              {unitsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="spinner" />
                </div>
              ) : units.length === 0 ? (
                <p className="text-tactical-muted text-center py-8">No units registered</p>
              ) : (
                units.slice(0, 10).map((unit) => <UnitItem key={unit.id} unit={unit} />)
              )}
            </div>
          </div>
        </div>

        {/* Situation Assessment */}
        {tacticalPicture && (
          <div className="panel mt-6">
            <div className="panel-header">
              <h2 className="panel-title">Situation Assessment</h2>
            </div>
            <div className="space-y-4">
              <p className="text-tactical-text">{tacticalPicture.situation_assessment.summary}</p>

              {tacticalPicture.recommendations && tacticalPicture.recommendations.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-tactical-primary mb-2">
                    RECOMMENDATIONS
                  </h3>
                  <ul className="space-y-1">
                    {tacticalPicture.recommendations.map((rec: string, idx: number) => (
                      <li key={idx} className="text-sm text-tactical-text flex items-start">
                        <span className="text-tactical-primary mr-2">▸</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

// Stat Card Component
interface StatCardProps {
  icon: React.ReactNode
  title: string
  value: string | number
  subtitle: string
  color: 'green' | 'amber' | 'red'
  loading: boolean
}

function StatCard({ icon, title, value, subtitle, color, loading }: StatCardProps) {
  const colorClasses = {
    green: 'text-status-green border-status-green',
    amber: 'text-status-amber border-status-amber',
    red: 'text-threat-high border-threat-high',
  }

  return (
    <div className={`panel border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-tactical-muted uppercase tracking-wide">{title}</p>
          {loading ? (
            <div className="spinner mt-2" />
          ) : (
            <>
              <p className={`text-3xl font-bold font-mono mt-2 ${colorClasses[color]}`}>
                {value}
              </p>
              <p className="text-xs text-tactical-muted mt-1 truncate">{subtitle}</p>
            </>
          )}
        </div>
        <div className={colorClasses[color]}>{icon}</div>
      </div>
    </div>
  )
}

// Threat Item Component
function ThreatItem({ threat }: { threat: any }) {
  const levelColors: Record<string, string> = {
    low: 'badge-low',
    medium: 'badge-medium',
    high: 'badge-high',
    critical: 'badge-critical',
  }

  return (
    <div className="bg-tactical-bg border border-tactical-border rounded p-3 hover:bg-tactical-hover transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <span className={`badge ${levelColors[threat.threat_level]}`}>
              {threat.threat_level}
            </span>
            <span className="badge bg-tactical-surface text-tactical-text">
              {threat.threat_type}
            </span>
          </div>
          <p className="text-sm text-tactical-text">{threat.description || 'No description'}</p>
          <p className="text-xs text-tactical-muted mt-1 font-mono">
            {new Date(threat.detected_at).toLocaleString()} • {threat.source}
          </p>
        </div>
      </div>
    </div>
  )
}

// Unit Item Component
function UnitItem({ unit }: { unit: any }) {
  const statusColors: Record<string, string> = {
    green: 'badge-green',
    amber: 'badge-amber',
    red: 'badge-red',
    black: 'bg-status-black text-white',
  }

  return (
    <div className="bg-tactical-bg border border-tactical-border rounded p-3 hover:bg-tactical-hover transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <span className="font-semibold text-tactical-primary font-mono">
              {unit.unit_id}
            </span>
            <span className={`badge ${statusColors[unit.status]}`}>{unit.status}</span>
          </div>
          <p className="text-sm text-tactical-text">{unit.unit_name}</p>
          <p className="text-xs text-tactical-muted mt-1 font-mono">
            {unit.callsign || 'No callsign'} • Last contact:{' '}
            {new Date(unit.last_contact).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
