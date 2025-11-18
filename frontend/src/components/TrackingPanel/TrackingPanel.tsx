/**
 * Tracking Panel Component
 * Friendly force tracking and blue-on-blue prevention
 */

import { useState } from 'react'
import { useTrackingData } from '@/hooks'
import {
  Shield,
  Plus,
  Search,
  X,
  Eye,
  MapPin,
  AlertCircle,
  Users,
} from 'lucide-react'
import type { FriendlyForce, FriendlyForceCreate } from '@/types'
import { apiClient } from '@/services/api'
import { useQueryClient } from '@tanstack/react-query'

function TrackingPanel() {
  const queryClient = useQueryClient()
  const { units, isLoading } = useTrackingData()
  const [selectedUnit, setSelectedUnit] = useState<FriendlyForce | null>(null)
  const [showAddUnit, setShowAddUnit] = useState(false)
  const [showBlueOnBlue, setShowBlueOnBlue] = useState(false)

  // Filters
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Filter units
  const filteredUnits = units.filter((unit) => {
    const matchesStatus = filterStatus === 'all' || unit.status === filterStatus
    const matchesType = filterType === 'all' || unit.unit_type === filterType
    const matchesSearch =
      !searchQuery ||
      unit.unit_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      unit.unit_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      unit.callsign?.toLowerCase().includes(searchQuery.toLowerCase())

    return matchesStatus && matchesType && matchesSearch
  })

  // Count by status
  const statusCounts = {
    green: units.filter((u) => u.status === 'green').length,
    amber: units.filter((u) => u.status === 'amber').length,
    red: units.filter((u) => u.status === 'red').length,
    black: units.filter((u) => u.status === 'black').length,
  }

  // Active units
  const activeUnits = units.filter((u) => u.active).length

  return (
    <div className="h-full flex flex-col bg-tactical-bg">
      {/* Header */}
      <header className="bg-tactical-surface border-b border-tactical-border px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Shield className="w-6 h-6 text-status-green" />
            <div>
              <h1 className="text-xl font-bold text-tactical-primary font-mono">
                FORCE TRACKING
              </h1>
              <p className="text-xs text-tactical-muted">
                Friendly Force Management & Blue-on-Blue Prevention
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowBlueOnBlue(true)}
              className="btn-secondary flex items-center space-x-2 text-sm"
            >
              <AlertCircle className="w-4 h-4" />
              <span>Blue-on-Blue Check</span>
            </button>

            <button
              onClick={() => setShowAddUnit(true)}
              className="btn-primary flex items-center space-x-2 text-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Add Unit</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Unit List */}
        <div className="w-96 border-r border-tactical-border flex flex-col bg-tactical-surface">
          {/* Filters */}
          <div className="p-4 border-b border-tactical-border space-y-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-tactical-muted" />
              <input
                type="text"
                placeholder="Search units..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10 text-sm"
              />
            </div>

            {/* Status Filter */}
            <div>
              <label className="text-xs text-tactical-muted uppercase mb-1 block">
                Status
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="select text-sm"
              >
                <option value="all">All Status ({units.length})</option>
                <option value="green">Green ({statusCounts.green})</option>
                <option value="amber">Amber ({statusCounts.amber})</option>
                <option value="red">Red ({statusCounts.red})</option>
                <option value="black">Black ({statusCounts.black})</option>
              </select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="text-xs text-tactical-muted uppercase mb-1 block">
                Unit Type
              </label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="select text-sm"
              >
                <option value="all">All Types</option>
                <option value="infantry">Infantry</option>
                <option value="armor">Armor</option>
                <option value="artillery">Artillery</option>
                <option value="aviation">Aviation</option>
                <option value="logistics">Logistics</option>
                <option value="medical">Medical</option>
                <option value="engineer">Engineer</option>
                <option value="headquarters">Headquarters</option>
                <option value="reconnaissance">Reconnaissance</option>
              </select>
            </div>

            {/* Stats */}
            <div className="pt-2 border-t border-tactical-border space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-tactical-muted">Active</span>
                <span className="font-mono font-bold text-status-green">
                  {activeUnits} / {units.length}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-tactical-muted">Showing</span>
                <span className="font-mono font-bold text-tactical-primary">
                  {filteredUnits.length} / {units.length}
                </span>
              </div>
            </div>
          </div>

          {/* Unit List */}
          <div className="flex-1 overflow-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="spinner" />
              </div>
            ) : filteredUnits.length === 0 ? (
              <div className="text-center py-12">
                <Shield className="w-12 h-12 text-tactical-muted mx-auto mb-3 opacity-50" />
                <p className="text-tactical-muted text-sm">
                  {searchQuery || filterStatus !== 'all' || filterType !== 'all'
                    ? 'No units match your filters'
                    : 'No units registered'}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-tactical-border">
                {filteredUnits.map((unit) => (
                  <UnitListItem
                    key={unit.unit_id}
                    unit={unit}
                    isSelected={selectedUnit?.unit_id === unit.unit_id}
                    onClick={() => setSelectedUnit(unit)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main Panel - Unit Details */}
        <div className="flex-1 overflow-auto">
          {selectedUnit ? (
            <UnitDetails
              unit={selectedUnit}
              onClose={() => setSelectedUnit(null)}
              onUpdate={() => {
                queryClient.invalidateQueries({ queryKey: ['units'] })
                setSelectedUnit(null)
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Eye className="w-16 h-16 text-tactical-muted mx-auto mb-4 opacity-30" />
                <p className="text-tactical-muted">
                  Select a unit to view details
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add Unit Modal */}
      {showAddUnit && (
        <AddUnitModal
          onClose={() => setShowAddUnit(false)}
          onSuccess={() => {
            setShowAddUnit(false)
            queryClient.invalidateQueries({ queryKey: ['units'] })
          }}
        />
      )}

      {/* Blue-on-Blue Check Modal */}
      {showBlueOnBlue && (
        <BlueOnBlueModal onClose={() => setShowBlueOnBlue(false)} />
      )}
    </div>
  )
}

// Unit List Item
interface UnitListItemProps {
  unit: FriendlyForce
  isSelected: boolean
  onClick: () => void
}

function UnitListItem({ unit, isSelected, onClick }: UnitListItemProps) {
  const statusColors: Record<string, string> = {
    green: 'badge-green',
    amber: 'badge-amber',
    red: 'badge-red',
    black: 'bg-status-black text-white',
  }

  return (
    <div
      onClick={onClick}
      className={`p-4 cursor-pointer transition-colors ${
        isSelected
          ? 'bg-tactical-primary bg-opacity-10 border-l-4 border-tactical-primary'
          : 'hover:bg-tactical-hover'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <span className={`badge ${statusColors[unit.status]} text-xs`}>
          {unit.status}
        </span>
        <span className="text-xs text-tactical-muted">
          {unit.active ? '● ACTIVE' : '○ INACTIVE'}
        </span>
      </div>
      <div className="mb-1">
        <span className="text-sm font-semibold text-tactical-text font-mono">
          {unit.unit_id}
        </span>
      </div>
      <p className="text-xs text-tactical-text mb-1">{unit.unit_name}</p>
      {unit.callsign && (
        <p className="text-xs text-tactical-muted">Callsign: {unit.callsign}</p>
      )}
      <div className="flex items-center justify-between text-xs text-tactical-muted mt-2">
        <span>{unit.unit_type}</span>
        <span className="flex items-center">
          <Users className="w-3 h-3 mr-1" />
          {unit.personnel_count}
        </span>
      </div>
    </div>
  )
}

// Unit Details Panel
interface UnitDetailsProps {
  unit: FriendlyForce
  onClose: () => void
  onUpdate: () => void
}

function UnitDetails({ unit, onClose, onUpdate }: UnitDetailsProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [status, setStatus] = useState(unit.status)
  const [latitude, setLatitude] = useState(unit.latitude.toString())
  const [longitude, setLongitude] = useState(unit.longitude.toString())
  const [isUpdating, setIsUpdating] = useState(false)

  const handleUpdate = async () => {
    setIsUpdating(true)
    try {
      await apiClient.updateUnitPosition(unit.unit_id, {
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        status: status as any,
      })
      onUpdate()
    } catch (error) {
      console.error('Update failed:', error)
      alert('Failed to update unit. Please try again.')
    } finally {
      setIsUpdating(false)
    }
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h2 className="text-2xl font-bold text-tactical-primary font-mono">
              {unit.unit_id}
            </h2>
            <span className={`badge badge-${unit.status}`}>
              {unit.status}
            </span>
            {unit.active && (
              <span className="badge badge-green text-xs">ACTIVE</span>
            )}
          </div>
          <p className="text-sm text-tactical-muted">
            Last contact {new Date(unit.last_contact).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="btn-secondary text-sm"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
          <button
            onClick={onClose}
            className="text-tactical-muted hover:text-tactical-text"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="panel">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Unit Information
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-tactical-muted">Name:</span>
              <span className="font-semibold text-tactical-text">
                {unit.unit_name}
              </span>
            </div>
            {unit.callsign && (
              <div className="flex justify-between">
                <span className="text-tactical-muted">Callsign:</span>
                <span className="font-mono font-semibold text-tactical-text">
                  {unit.callsign}
                </span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-tactical-muted">Type:</span>
              <span className="font-semibold text-tactical-text capitalize">
                {unit.unit_type}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-tactical-muted">Personnel:</span>
              <span className="font-mono font-semibold text-tactical-text">
                {unit.personnel_count}
              </span>
            </div>
          </div>
        </div>

        <div className="panel">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Position
          </h3>
          <div className="space-y-2 text-sm">
            {isEditing ? (
              <>
                <div>
                  <label className="text-xs text-tactical-muted block mb-1">
                    Latitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    className="input text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-tactical-muted block mb-1">
                    Longitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    className="input text-sm"
                  />
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-tactical-muted">Latitude:</span>
                  <span className="font-mono text-tactical-text">
                    {unit.latitude.toFixed(6)}°
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-tactical-muted">Longitude:</span>
                  <span className="font-mono text-tactical-text">
                    {unit.longitude.toFixed(6)}°
                  </span>
                </div>
              </>
            )}
            {unit.altitude && (
              <div className="flex justify-between">
                <span className="text-tactical-muted">Altitude:</span>
                <span className="font-mono text-tactical-text">
                  {unit.altitude.toFixed(1)}m
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Status Update */}
      {isEditing && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Update Status
          </h3>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-tactical-muted uppercase mb-1 block">
                Status
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as any)}
                className="select"
              >
                <option value="green">Green - Fully Operational</option>
                <option value="amber">Amber - Partially Operational</option>
                <option value="red">Red - Not Operational</option>
                <option value="black">Black - Destroyed/Lost</option>
              </select>
            </div>
            <button
              onClick={handleUpdate}
              disabled={isUpdating}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {isUpdating && <div className="spinner" />}
              <span>{isUpdating ? 'Updating...' : 'Update Position & Status'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Mission */}
      {unit.mission && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Mission
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed">
            {unit.mission}
          </p>
        </div>
      )}

      {/* Equipment */}
      {unit.equipment && unit.equipment.length > 0 && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Equipment
          </h3>
          <ul className="space-y-1">
            {unit.equipment.map((item: string, idx: number) => (
              <li key={idx} className="text-sm text-tactical-text flex items-start">
                <span className="text-tactical-primary mr-2">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Metadata */}
      <div className="panel">
        <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
          Metadata
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-tactical-muted block mb-1">Created:</span>
            <span className="font-mono text-tactical-text">
              {new Date(unit.created_at).toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-tactical-muted block mb-1">Last Contact:</span>
            <span className="font-mono text-tactical-text">
              {new Date(unit.last_contact).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Add Unit Modal
function AddUnitModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [unitId, setUnitId] = useState('')
  const [unitName, setUnitName] = useState('')
  const [callsign, setCallsign] = useState('')
  const [unitType, setUnitType] = useState<string>('infantry')
  const [personnelCount, setPersonnelCount] = useState('10')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [mission, setMission] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const handleCreate = async () => {
    if (!unitId || !unitName || !latitude || !longitude) return

    setIsCreating(true)
    try {
      const unitData: FriendlyForceCreate = {
        unit_id: unitId,
        unit_name: unitName,
        callsign: callsign || undefined,
        unit_type: unitType as any,
        personnel_count: parseInt(personnelCount),
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        mission: mission || undefined,
      }

      await apiClient.createUnit(unitData)
      onSuccess()
    } catch (error) {
      console.error('Creation failed:', error)
      alert('Failed to create unit. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-tactical-surface border border-tactical-border rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-tactical-surface border-b border-tactical-border px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Plus className="w-5 h-5 text-tactical-primary" />
            <h2 className="text-lg font-bold text-tactical-primary font-mono">
              ADD FRIENDLY UNIT
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-tactical-muted hover:text-tactical-text"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-tactical-muted uppercase mb-2 block">
                Unit ID *
              </label>
              <input
                type="text"
                value={unitId}
                onChange={(e) => setUnitId(e.target.value)}
                placeholder="e.g., 1-502-INF"
                className="input"
              />
            </div>

            <div>
              <label className="text-sm text-tactical-muted uppercase mb-2 block">
                Unit Name *
              </label>
              <input
                type="text"
                value={unitName}
                onChange={(e) => setUnitName(e.target.value)}
                placeholder="e.g., 1st Battalion, 502nd Infantry"
                className="input"
              />
            </div>

            <div>
              <label className="text-sm text-tactical-muted uppercase mb-2 block">
                Callsign
              </label>
              <input
                type="text"
                value={callsign}
                onChange={(e) => setCallsign(e.target.value)}
                placeholder="e.g., Strike 6"
                className="input"
              />
            </div>

            <div>
              <label className="text-sm text-tactical-muted uppercase mb-2 block">
                Unit Type *
              </label>
              <select
                value={unitType}
                onChange={(e) => setUnitType(e.target.value)}
                className="select"
              >
                <option value="infantry">Infantry</option>
                <option value="armor">Armor</option>
                <option value="artillery">Artillery</option>
                <option value="aviation">Aviation</option>
                <option value="logistics">Logistics</option>
                <option value="medical">Medical</option>
                <option value="engineer">Engineer</option>
                <option value="headquarters">Headquarters</option>
                <option value="reconnaissance">Reconnaissance</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-tactical-muted uppercase mb-2 block">
                Personnel Count *
              </label>
              <input
                type="number"
                value={personnelCount}
                onChange={(e) => setPersonnelCount(e.target.value)}
                className="input"
              />
            </div>

            <div className="col-span-2 grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Latitude *
                </label>
                <input
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  placeholder="0.000000"
                  className="input"
                />
              </div>
              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Longitude *
                </label>
                <input
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  placeholder="0.000000"
                  className="input"
                />
              </div>
            </div>

            <div className="col-span-2">
              <label className="text-sm text-tactical-muted uppercase mb-2 block">
                Mission
              </label>
              <textarea
                value={mission}
                onChange={(e) => setMission(e.target.value)}
                placeholder="Current mission or task"
                rows={3}
                className="textarea"
              />
            </div>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4">
            <button onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={isCreating || !unitId || !unitName || !latitude || !longitude}
              className="btn-primary flex items-center space-x-2"
            >
              {isCreating && <div className="spinner" />}
              <Plus className="w-4 h-4" />
              <span>{isCreating ? 'Creating...' : 'Create Unit'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Blue-on-Blue Check Modal (simplified)
function BlueOnBlueModal({ onClose }: { onClose: () => void }) {
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [radius, setRadius] = useState('1000')
  const [isChecking, setIsChecking] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleCheck = async () => {
    if (!latitude || !longitude) return

    setIsChecking(true)
    setResult(null)

    try {
      const response = await apiClient.checkBlueOnBlue({
        target_latitude: parseFloat(latitude),
        target_longitude: parseFloat(longitude),
        radius_meters: parseInt(radius),
      })
      setResult(response)
    } catch (error) {
      console.error('Check failed:', error)
      alert('Blue-on-blue check failed. Please try again.')
    } finally {
      setIsChecking(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-tactical-surface border border-tactical-border rounded-lg max-w-2xl w-full">
        <div className="px-6 py-4 border-b border-tactical-border flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-tactical-primary" />
            <h2 className="text-lg font-bold text-tactical-primary font-mono">
              BLUE-ON-BLUE CHECK
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-tactical-muted hover:text-tactical-text"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {!result ? (
            <>
              <div className="alert-warning">
                <p className="text-sm">
                  Check if any friendly forces are near the target coordinates to prevent
                  blue-on-blue incidents.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-tactical-muted uppercase mb-2 block">
                    Target Latitude *
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    placeholder="0.000000"
                    className="input"
                  />
                </div>
                <div>
                  <label className="text-sm text-tactical-muted uppercase mb-2 block">
                    Target Longitude *
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    placeholder="0.000000"
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Check Radius (meters)
                </label>
                <select
                  value={radius}
                  onChange={(e) => setRadius(e.target.value)}
                  className="select"
                >
                  <option value="500">500m - Danger Zone</option>
                  <option value="1000">1000m - Warning Zone</option>
                  <option value="2000">2000m - Caution Zone</option>
                  <option value="5000">5000m - Extended</option>
                </select>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button onClick={onClose} className="btn-secondary">
                  Cancel
                </button>
                <button
                  onClick={handleCheck}
                  disabled={isChecking || !latitude || !longitude}
                  className="btn-primary flex items-center space-x-2"
                >
                  {isChecking && <div className="spinner" />}
                  <AlertCircle className="w-4 h-4" />
                  <span>{isChecking ? 'Checking...' : 'Check'}</span>
                </button>
              </div>
            </>
          ) : (
            <>
              {result.alerts && result.alerts.length > 0 ? (
                <div className="alert-danger">
                  <p className="font-semibold mb-2">
                    ⚠️ FRIENDLIES DETECTED IN AREA
                  </p>
                  <p className="text-sm">
                    {result.alerts.length} alert(s) - Review before proceeding
                  </p>
                </div>
              ) : (
                <div className="alert-success">
                  <p className="font-semibold mb-1">✓ All Clear</p>
                  <p className="text-sm">No friendly forces detected in target area</p>
                </div>
              )}

              {result.nearby_units && result.nearby_units.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold text-tactical-primary uppercase">
                    Nearby Units ({result.nearby_units.length})
                  </h4>
                  {result.nearby_units.map((unit: any, idx: number) => (
                    <div key={idx} className="panel text-sm">
                      <div className="font-mono font-bold text-tactical-text mb-1">
                        {unit.unit_id}
                      </div>
                      <div className="text-tactical-muted">
                        Distance: {unit.distance.toFixed(0)}m • Status: {unit.status}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button onClick={onClose} className="btn-primary">
                  Close
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default TrackingPanel
