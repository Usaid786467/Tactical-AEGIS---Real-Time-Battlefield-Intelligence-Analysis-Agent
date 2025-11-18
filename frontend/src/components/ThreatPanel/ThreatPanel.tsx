/**
 * Threat Analysis Panel Component
 * Comprehensive threat management and analysis interface
 */

import { useState } from 'react'
import { useThreatData } from '@/hooks'
import {
  AlertTriangle,
  Filter,
  Image as ImageIcon,
  TrendingUp,
  Upload,
  X,
  Eye,
  Search,
} from 'lucide-react'
import type { Threat, ThreatLevel, ThreatType } from '@/types'
import { apiClient } from '@/services/api'

function ThreatPanel() {
  const { threats, isLoading } = useThreatData()
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null)
  const [showImageAnalyzer, setShowImageAnalyzer] = useState(false)
  const [showPrediction, setShowPrediction] = useState(false)

  // Filters
  const [filterLevel, setFilterLevel] = useState<ThreatLevel | 'all'>('all')
  const [filterType, setFilterType] = useState<ThreatType | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Filter threats
  const filteredThreats = threats.filter((threat) => {
    const matchesLevel = filterLevel === 'all' || threat.threat_level === filterLevel
    const matchesType = filterType === 'all' || threat.threat_type === filterType
    const matchesSearch =
      !searchQuery ||
      threat.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      threat.source.toLowerCase().includes(searchQuery.toLowerCase())

    return matchesLevel && matchesType && matchesSearch
  })

  // Count by level
  const threatCounts = {
    critical: threats.filter((t) => t.threat_level === 'critical').length,
    high: threats.filter((t) => t.threat_level === 'high').length,
    medium: threats.filter((t) => t.threat_level === 'medium').length,
    low: threats.filter((t) => t.threat_level === 'low').length,
  }

  return (
    <div className="h-full flex flex-col bg-tactical-bg">
      {/* Header */}
      <header className="bg-tactical-surface border-b border-tactical-border px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <AlertTriangle className="w-6 h-6 text-threat-high" />
            <div>
              <h1 className="text-xl font-bold text-tactical-primary font-mono">
                THREAT ANALYSIS
              </h1>
              <p className="text-xs text-tactical-muted">
                Intelligence & Predictive Analysis
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowImageAnalyzer(true)}
              className="btn-primary flex items-center space-x-2 text-sm"
            >
              <ImageIcon className="w-4 h-4" />
              <span>Analyze Image</span>
            </button>

            <button
              onClick={() => setShowPrediction(true)}
              className="btn-secondary flex items-center space-x-2 text-sm"
            >
              <TrendingUp className="w-4 h-4" />
              <span>Predict Threats</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Threat List */}
        <div className="w-96 border-r border-tactical-border flex flex-col bg-tactical-surface">
          {/* Filters */}
          <div className="p-4 border-b border-tactical-border space-y-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-tactical-muted" />
              <input
                type="text"
                placeholder="Search threats..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10 text-sm"
              />
            </div>

            {/* Level Filter */}
            <div>
              <label className="text-xs text-tactical-muted uppercase mb-1 block">
                Threat Level
              </label>
              <select
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value as ThreatLevel | 'all')}
                className="select text-sm"
              >
                <option value="all">All Levels ({threats.length})</option>
                <option value="critical">Critical ({threatCounts.critical})</option>
                <option value="high">High ({threatCounts.high})</option>
                <option value="medium">Medium ({threatCounts.medium})</option>
                <option value="low">Low ({threatCounts.low})</option>
              </select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="text-xs text-tactical-muted uppercase mb-1 block">
                Threat Type
              </label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as ThreatType | 'all')}
                className="select text-sm"
              >
                <option value="all">All Types</option>
                <option value="vehicle">Vehicle</option>
                <option value="personnel">Personnel</option>
                <option value="weapon">Weapon</option>
                <option value="ied">IED</option>
                <option value="artillery">Artillery</option>
                <option value="aircraft">Aircraft</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>

            {/* Stats */}
            <div className="pt-2 border-t border-tactical-border">
              <div className="flex items-center justify-between text-xs">
                <span className="text-tactical-muted">Showing</span>
                <span className="font-mono font-bold text-tactical-primary">
                  {filteredThreats.length} / {threats.length}
                </span>
              </div>
            </div>
          </div>

          {/* Threat List */}
          <div className="flex-1 overflow-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="spinner" />
              </div>
            ) : filteredThreats.length === 0 ? (
              <div className="text-center py-12">
                <AlertTriangle className="w-12 h-12 text-tactical-muted mx-auto mb-3 opacity-50" />
                <p className="text-tactical-muted text-sm">
                  {searchQuery || filterLevel !== 'all' || filterType !== 'all'
                    ? 'No threats match your filters'
                    : 'No threats detected'}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-tactical-border">
                {filteredThreats.map((threat) => (
                  <ThreatListItem
                    key={threat.id}
                    threat={threat}
                    isSelected={selectedThreat?.id === threat.id}
                    onClick={() => setSelectedThreat(threat)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main Panel - Threat Details */}
        <div className="flex-1 overflow-auto">
          {selectedThreat ? (
            <ThreatDetails
              threat={selectedThreat}
              onClose={() => setSelectedThreat(null)}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Eye className="w-16 h-16 text-tactical-muted mx-auto mb-4 opacity-30" />
                <p className="text-tactical-muted">
                  Select a threat to view details
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Image Analyzer Modal */}
      {showImageAnalyzer && (
        <ImageAnalyzerModal onClose={() => setShowImageAnalyzer(false)} />
      )}

      {/* Prediction Modal */}
      {showPrediction && (
        <PredictionModal onClose={() => setShowPrediction(false)} />
      )}
    </div>
  )
}

// Threat List Item
interface ThreatListItemProps {
  threat: Threat
  isSelected: boolean
  onClick: () => void
}

function ThreatListItem({ threat, isSelected, onClick }: ThreatListItemProps) {
  const levelColors: Record<string, string> = {
    low: 'badge-low',
    medium: 'badge-medium',
    high: 'badge-high',
    critical: 'badge-critical',
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
        <span className={`badge ${levelColors[threat.threat_level]} text-xs`}>
          {threat.threat_level}
        </span>
        <span className="text-xs text-tactical-muted font-mono">
          #{threat.id}
        </span>
      </div>
      <div className="mb-1">
        <span className="text-sm font-semibold text-tactical-text">
          {threat.threat_type.toUpperCase()}
        </span>
      </div>
      <p className="text-xs text-tactical-muted line-clamp-2 mb-2">
        {threat.description || 'No description available'}
      </p>
      <div className="flex items-center justify-between text-xs text-tactical-muted">
        <span>{threat.source}</span>
        <span>{new Date(threat.detected_at).toLocaleTimeString()}</span>
      </div>
    </div>
  )
}

// Threat Details Panel
interface ThreatDetailsProps {
  threat: Threat
  onClose: () => void
}

function ThreatDetails({ threat, onClose }: ThreatDetailsProps) {
  const levelColors: Record<string, string> = {
    low: 'text-threat-low',
    medium: 'text-threat-medium',
    high: 'text-threat-high',
    critical: 'text-threat-critical',
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h2 className="text-2xl font-bold text-tactical-primary font-mono">
              THREAT #{threat.id}
            </h2>
            <span className={`badge badge-${threat.threat_level}`}>
              {threat.threat_level}
            </span>
          </div>
          <p className="text-sm text-tactical-muted">
            Detected {new Date(threat.detected_at).toLocaleString()}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-tactical-muted hover:text-tactical-text"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="panel">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Classification
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-tactical-muted">Type:</span>
              <span className="font-semibold text-tactical-text">
                {threat.threat_type.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-tactical-muted">Level:</span>
              <span className={`font-semibold ${levelColors[threat.threat_level]}`}>
                {threat.threat_level.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-tactical-muted">Confidence:</span>
              <span className="font-mono font-semibold text-tactical-text">
                {(threat.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-tactical-muted">Status:</span>
              <span
                className={`font-semibold ${
                  threat.active ? 'text-status-green' : 'text-tactical-muted'
                }`}
              >
                {threat.active ? 'ACTIVE' : 'INACTIVE'}
              </span>
            </div>
          </div>
        </div>

        <div className="panel">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Location
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-tactical-muted">Latitude:</span>
              <span className="font-mono text-tactical-text">
                {threat.latitude.toFixed(6)}°
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-tactical-muted">Longitude:</span>
              <span className="font-mono text-tactical-text">
                {threat.longitude.toFixed(6)}°
              </span>
            </div>
            {threat.altitude && (
              <div className="flex justify-between">
                <span className="text-tactical-muted">Altitude:</span>
                <span className="font-mono text-tactical-text">
                  {threat.altitude.toFixed(1)}m
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Description */}
      {threat.description && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Description
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed">
            {threat.description}
          </p>
        </div>
      )}

      {/* Metadata */}
      <div className="panel">
        <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
          Metadata
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-tactical-muted block mb-1">Source:</span>
            <span className="font-mono text-tactical-text">{threat.source}</span>
          </div>
          <div>
            <span className="text-tactical-muted block mb-1">Detected At:</span>
            <span className="font-mono text-tactical-text">
              {new Date(threat.detected_at).toLocaleString()}
            </span>
          </div>
          {threat.image_url && (
            <div className="col-span-2">
              <span className="text-tactical-muted block mb-2">Image:</span>
              <img
                src={threat.image_url}
                alt="Threat"
                className="rounded border border-tactical-border max-h-64 w-auto"
              />
            </div>
          )}
          {threat.metadata && Object.keys(threat.metadata).length > 0 && (
            <div className="col-span-2">
              <span className="text-tactical-muted block mb-1">Additional Data:</span>
              <pre className="bg-tactical-bg p-3 rounded text-xs font-mono overflow-auto max-h-40">
                {JSON.stringify(threat.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Image Analyzer Modal
function ImageAnalyzerModal({ onClose }: { onClose: () => void }) {
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imageUrl, setImageUrl] = useState('')
  const [source, setSource] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleAnalyze = async () => {
    if ((!imageFile && !imageUrl) || !source) return

    setIsAnalyzing(true)
    setResult(null)

    try {
      let imageData = null
      if (imageFile) {
        const reader = new FileReader()
        imageData = await new Promise((resolve) => {
          reader.onload = (e) => resolve(e.target?.result as string)
          reader.readAsDataURL(imageFile)
        })
      }

      const response = await apiClient.analyzeImage({
        image_data: imageData as string | undefined,
        image_url: imageUrl || undefined,
        source,
        location: latitude && longitude ? {
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
        } : undefined,
      })

      setResult(response)
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-tactical-surface border border-tactical-border rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="sticky top-0 bg-tactical-surface border-b border-tactical-border px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ImageIcon className="w-5 h-5 text-tactical-primary" />
            <h2 className="text-lg font-bold text-tactical-primary font-mono">
              IMAGE ANALYZER
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-tactical-muted hover:text-tactical-text"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {!result ? (
            <>
              {/* Image Upload */}
              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Upload Image
                </label>
                <div className="border-2 border-dashed border-tactical-border rounded-lg p-8 text-center">
                  <Upload className="w-12 h-12 text-tactical-muted mx-auto mb-3" />
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="image-upload"
                  />
                  <label
                    htmlFor="image-upload"
                    className="btn-secondary cursor-pointer inline-block"
                  >
                    Choose File
                  </label>
                  {imageFile && (
                    <p className="text-sm text-tactical-text mt-2">{imageFile.name}</p>
                  )}
                </div>
              </div>

              {/* Or Image URL */}
              <div className="text-center text-tactical-muted text-sm">OR</div>

              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Image URL
                </label>
                <input
                  type="url"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  placeholder="https://example.com/image.jpg"
                  className="input"
                />
              </div>

              {/* Source */}
              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Source *
                </label>
                <input
                  type="text"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  placeholder="e.g., Satellite, Drone, Ground Recon"
                  className="input"
                />
              </div>

              {/* Location */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-tactical-muted uppercase mb-2 block">
                    Latitude
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
                    Longitude
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

              {/* Actions */}
              <div className="flex items-center justify-end space-x-3 pt-4">
                <button onClick={onClose} className="btn-secondary">
                  Cancel
                </button>
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || (!imageFile && !imageUrl) || !source}
                  className="btn-primary flex items-center space-x-2"
                >
                  {isAnalyzing && <div className="spinner" />}
                  <span>{isAnalyzing ? 'Analyzing...' : 'Analyze'}</span>
                </button>
              </div>
            </>
          ) : (
            <>
              {/* Results */}
              <div className="alert-success">
                <p className="font-semibold mb-1">Analysis Complete</p>
                <p className="text-sm">
                  Detected {result.threats?.length || 0} threat(s)
                </p>
              </div>

              {result.threats && result.threats.length > 0 && (
                <div className="space-y-3">
                  {result.threats.map((threat: any, idx: number) => (
                    <div key={idx} className="panel">
                      <div className="flex items-start justify-between mb-2">
                        <span className={`badge badge-${threat.threat_level}`}>
                          {threat.threat_level}
                        </span>
                        <span className="text-xs text-tactical-muted">
                          {(threat.confidence * 100).toFixed(1)}% confidence
                        </span>
                      </div>
                      <p className="text-sm font-semibold text-tactical-text mb-1">
                        {threat.threat_type}
                      </p>
                      <p className="text-xs text-tactical-muted">
                        {threat.description}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button onClick={onClose} className="btn-primary">
                  Done
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// Prediction Modal (simplified)
function PredictionModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-tactical-surface border border-tactical-border rounded-lg max-w-2xl w-full">
        <div className="px-6 py-4 border-b border-tactical-border flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-5 h-5 text-tactical-primary" />
            <h2 className="text-lg font-bold text-tactical-primary font-mono">
              THREAT PREDICTION
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-tactical-muted hover:text-tactical-text"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">
          <p className="text-tactical-muted text-sm text-center">
            Threat prediction interface coming soon...
          </p>
          <div className="flex justify-end mt-6">
            <button onClick={onClose} className="btn-secondary">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ThreatPanel
