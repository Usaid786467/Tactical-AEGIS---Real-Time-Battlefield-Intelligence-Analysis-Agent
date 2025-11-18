/**
 * SITREP Panel Component
 * Situation Report generation and management interface
 */

import { useState } from 'react'
import { apiClient } from '@/services/api'
import {
  FileText,
  Mic,
  Plus,
  Search,
  X,
  Eye,
  Sparkles,
  MicOff,
} from 'lucide-react'
import type { Sitrep } from '@/types'
import { SitrepPriority } from '@/types'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

function SitrepPanel() {
  const queryClient = useQueryClient()
  const [selectedSitrep, setSelectedSitrep] = useState<Sitrep | null>(null)
  const [showGenerator, setShowGenerator] = useState(false)
  const [showVoiceDebrief, setShowVoiceDebrief] = useState(false)

  // Filters
  const [filterPriority, setFilterPriority] = useState<SitrepPriority | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch SITREPs
  const { data: sitreps = [], isLoading } = useQuery({
    queryKey: ['sitreps'],
    queryFn: () => apiClient.getSitreps(),
  })

  // Filter SITREPs
  const filteredSitreps = sitreps.filter((sitrep) => {
    const matchesPriority = filterPriority === 'all' || sitrep.priority === filterPriority
    const matchesSearch =
      !searchQuery ||
      sitrep.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sitrep.summary?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sitrep.source.toLowerCase().includes(searchQuery.toLowerCase())

    return matchesPriority && matchesSearch
  })

  // Count by priority
  const priorityCounts = {
    routine: sitreps.filter((s) => s.priority === 'routine').length,
    priority: sitreps.filter((s) => s.priority === 'priority').length,
    immediate: sitreps.filter((s) => s.priority === 'immediate').length,
    flash: sitreps.filter((s) => s.priority === 'flash').length,
  }

  return (
    <div className="h-full flex flex-col bg-tactical-bg">
      {/* Header */}
      <header className="bg-tactical-surface border-b border-tactical-border px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <FileText className="w-6 h-6 text-tactical-primary" />
            <div>
              <h1 className="text-xl font-bold text-tactical-primary font-mono">
                SITUATION REPORTS
              </h1>
              <p className="text-xs text-tactical-muted">
                Automated SITREP Generation & Management
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowVoiceDebrief(true)}
              className="btn-secondary flex items-center space-x-2 text-sm"
            >
              <Mic className="w-4 h-4" />
              <span>Voice Debrief</span>
            </button>

            <button
              onClick={() => setShowGenerator(true)}
              className="btn-primary flex items-center space-x-2 text-sm"
            >
              <Sparkles className="w-4 h-4" />
              <span>Generate SITREP</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - SITREP List */}
        <div className="w-96 border-r border-tactical-border flex flex-col bg-tactical-surface">
          {/* Filters */}
          <div className="p-4 border-b border-tactical-border space-y-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-tactical-muted" />
              <input
                type="text"
                placeholder="Search SITREPs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10 text-sm"
              />
            </div>

            {/* Priority Filter */}
            <div>
              <label className="text-xs text-tactical-muted uppercase mb-1 block">
                Priority
              </label>
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value as SitrepPriority | 'all')}
                className="select text-sm"
              >
                <option value="all">All Priorities ({sitreps.length})</option>
                <option value="flash">Flash ({priorityCounts.flash})</option>
                <option value="immediate">Immediate ({priorityCounts.immediate})</option>
                <option value="priority">Priority ({priorityCounts.priority})</option>
                <option value="routine">Routine ({priorityCounts.routine})</option>
              </select>
            </div>

            {/* Stats */}
            <div className="pt-2 border-t border-tactical-border">
              <div className="flex items-center justify-between text-xs">
                <span className="text-tactical-muted">Showing</span>
                <span className="font-mono font-bold text-tactical-primary">
                  {filteredSitreps.length} / {sitreps.length}
                </span>
              </div>
            </div>
          </div>

          {/* SITREP List */}
          <div className="flex-1 overflow-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="spinner" />
              </div>
            ) : filteredSitreps.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-tactical-muted mx-auto mb-3 opacity-50" />
                <p className="text-tactical-muted text-sm">
                  {searchQuery || filterPriority !== 'all'
                    ? 'No SITREPs match your filters'
                    : 'No SITREPs generated'}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-tactical-border">
                {filteredSitreps.map((sitrep) => (
                  <SitrepListItem
                    key={sitrep.id}
                    sitrep={sitrep}
                    isSelected={selectedSitrep?.id === sitrep.id}
                    onClick={() => setSelectedSitrep(sitrep)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main Panel - SITREP Details */}
        <div className="flex-1 overflow-auto">
          {selectedSitrep ? (
            <SitrepDetails
              sitrep={selectedSitrep}
              onClose={() => setSelectedSitrep(null)}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Eye className="w-16 h-16 text-tactical-muted mx-auto mb-4 opacity-30" />
                <p className="text-tactical-muted">
                  Select a SITREP to view details
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* SITREP Generator Modal */}
      {showGenerator && (
        <SitrepGeneratorModal onClose={() => setShowGenerator(false)} />
      )}

      {/* Voice Debrief Modal */}
      {showVoiceDebrief && (
        <VoiceDebriefModal onClose={() => setShowVoiceDebrief(false)} />
      )}
    </div>
  )
}

// SITREP List Item
interface SitrepListItemProps {
  sitrep: Sitrep
  isSelected: boolean
  onClick: () => void
}

function SitrepListItem({ sitrep, isSelected, onClick }: SitrepListItemProps) {
  const priorityColors: Record<string, string> = {
    routine: 'badge-low',
    priority: 'badge-medium',
    immediate: 'badge-high',
    flash: 'badge-critical',
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
        <span className={`badge ${priorityColors[sitrep.priority]} text-xs`}>
          {sitrep.priority}
        </span>
        <span className="text-xs text-tactical-muted font-mono">
          #{sitrep.id}
        </span>
      </div>
      <div className="mb-1">
        <span className="text-sm font-semibold text-tactical-text">
          {sitrep.title || 'Untitled SITREP'}
        </span>
      </div>
      <p className="text-xs text-tactical-muted line-clamp-2 mb-2">
        {sitrep.summary || 'No summary available'}
      </p>
      <div className="flex items-center justify-between text-xs text-tactical-muted">
        <span>{sitrep.source}</span>
        <span>{new Date(sitrep.created_at).toLocaleTimeString()}</span>
      </div>
    </div>
  )
}

// SITREP Details Panel
interface SitrepDetailsProps {
  sitrep: Sitrep
  onClose: () => void
}

function SitrepDetails({ sitrep, onClose }: SitrepDetailsProps) {
  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h2 className="text-2xl font-bold text-tactical-primary font-mono">
              SITREP #{sitrep.id}
            </h2>
            <span className={`badge badge-${sitrep.priority}`}>
              {sitrep.priority}
            </span>
          </div>
          <p className="text-sm text-tactical-muted">
            Generated {new Date(sitrep.created_at).toLocaleString()}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-tactical-muted hover:text-tactical-text"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Title */}
      {sitrep.title && (
        <div className="panel mb-6">
          <h3 className="text-lg font-bold text-tactical-text">
            {sitrep.title}
          </h3>
        </div>
      )}

      {/* Summary */}
      {sitrep.summary && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Executive Summary
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed whitespace-pre-wrap">
            {sitrep.summary}
          </p>
        </div>
      )}

      {/* Situation */}
      {sitrep.situation && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Situation
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed whitespace-pre-wrap">
            {sitrep.situation}
          </p>
        </div>
      )}

      {/* Mission */}
      {sitrep.mission && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Mission
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed whitespace-pre-wrap">
            {sitrep.mission}
          </p>
        </div>
      )}

      {/* Execution */}
      {sitrep.execution && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Execution
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed whitespace-pre-wrap">
            {sitrep.execution}
          </p>
        </div>
      )}

      {/* Logistics */}
      {sitrep.logistics && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Logistics
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed whitespace-pre-wrap">
            {sitrep.logistics}
          </p>
        </div>
      )}

      {/* Command */}
      {sitrep.command && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Command & Signal
          </h3>
          <p className="text-sm text-tactical-text leading-relaxed whitespace-pre-wrap">
            {sitrep.command}
          </p>
        </div>
      )}

      {/* Recommendations */}
      {sitrep.recommendations && sitrep.recommendations.length > 0 && (
        <div className="panel mb-6">
          <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
            Recommendations
          </h3>
          <ul className="space-y-2">
            {sitrep.recommendations.map((rec: string, idx: number) => (
              <li key={idx} className="text-sm text-tactical-text flex items-start">
                <span className="text-tactical-primary mr-2">▸</span>
                {rec}
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
            <span className="text-tactical-muted block mb-1">Source:</span>
            <span className="font-mono text-tactical-text">{sitrep.source}</span>
          </div>
          <div>
            <span className="text-tactical-muted block mb-1">Priority:</span>
            <span className="font-mono text-tactical-text uppercase">{sitrep.priority}</span>
          </div>
          <div>
            <span className="text-tactical-muted block mb-1">Created:</span>
            <span className="font-mono text-tactical-text">
              {new Date(sitrep.created_at).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

// SITREP Generator Modal
function SitrepGeneratorModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [timeRange, setTimeRange] = useState('24')
  const [priority, setPriority] = useState<SitrepPriority>(SitrepPriority.ROUTINE)
  const [source, setSource] = useState('')
  const [includeThreats, setIncludeThreats] = useState(true)
  const [includeUnits, setIncludeUnits] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleGenerate = async () => {
    if (!source) return

    setIsGenerating(true)
    setResult(null)

    try {
      const response = await apiClient.generateSitrep({
        time_range_hours: parseInt(timeRange),
        priority,
        source,
        include_threats: includeThreats,
        include_units: includeUnits,
      })

      setResult(response)
      queryClient.invalidateQueries({ queryKey: ['sitreps'] })
    } catch (error) {
      console.error('Generation failed:', error)
      alert('SITREP generation failed. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-tactical-surface border border-tactical-border rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="sticky top-0 bg-tactical-surface border-b border-tactical-border px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-5 h-5 text-tactical-primary" />
            <h2 className="text-lg font-bold text-tactical-primary font-mono">
              AI SITREP GENERATOR
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
              <div className="alert-info">
                <p className="text-sm">
                  The AI will analyze recent tactical data and generate a comprehensive
                  situation report following military standards.
                </p>
              </div>

              {/* Time Range */}
              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Time Range (hours) *
                </label>
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="select"
                >
                  <option value="6">Last 6 hours</option>
                  <option value="12">Last 12 hours</option>
                  <option value="24">Last 24 hours</option>
                  <option value="48">Last 48 hours</option>
                  <option value="72">Last 72 hours</option>
                </select>
              </div>

              {/* Priority */}
              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Priority *
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as SitrepPriority)}
                  className="select"
                >
                  <option value="routine">Routine</option>
                  <option value="priority">Priority</option>
                  <option value="immediate">Immediate</option>
                  <option value="flash">Flash</option>
                </select>
              </div>

              {/* Source */}
              <div>
                <label className="text-sm text-tactical-muted uppercase mb-2 block">
                  Source / Author *
                </label>
                <input
                  type="text"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  placeholder="e.g., Battalion S2, TOC, Field Commander"
                  className="input"
                />
              </div>

              {/* Include Options */}
              <div className="space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeThreats}
                    onChange={(e) => setIncludeThreats(e.target.checked)}
                    className="form-checkbox h-4 w-4 text-tactical-primary bg-tactical-bg border-tactical-border rounded focus:ring-tactical-primary"
                  />
                  <span className="text-sm text-tactical-text">Include Threat Analysis</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeUnits}
                    onChange={(e) => setIncludeUnits(e.target.checked)}
                    className="form-checkbox h-4 w-4 text-tactical-primary bg-tactical-bg border-tactical-border rounded focus:ring-tactical-primary"
                  />
                  <span className="text-sm text-tactical-text">Include Force Disposition</span>
                </label>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end space-x-3 pt-4">
                <button onClick={onClose} className="btn-secondary">
                  Cancel
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={isGenerating || !source}
                  className="btn-primary flex items-center space-x-2"
                >
                  {isGenerating && <div className="spinner" />}
                  <Sparkles className="w-4 h-4" />
                  <span>{isGenerating ? 'Generating...' : 'Generate SITREP'}</span>
                </button>
              </div>
            </>
          ) : (
            <>
              {/* Success */}
              <div className="alert-success">
                <p className="font-semibold mb-1">SITREP Generated Successfully</p>
                <p className="text-sm">
                  SITREP #{result.id} has been created and saved.
                </p>
              </div>

              {/* Preview */}
              <div className="panel max-h-96 overflow-auto">
                <h3 className="text-sm font-semibold text-tactical-primary uppercase mb-3">
                  Preview
                </h3>
                {result.title && (
                  <h4 className="text-lg font-bold text-tactical-text mb-3">
                    {result.title}
                  </h4>
                )}
                {result.summary && (
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-tactical-primary mb-1">
                      SUMMARY
                    </p>
                    <p className="text-sm text-tactical-text whitespace-pre-wrap">
                      {result.summary}
                    </p>
                  </div>
                )}
              </div>

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

// Voice Debrief Modal (simplified)
function VoiceDebriefModal({ onClose }: { onClose: () => void }) {
  const [isRecording, setIsRecording] = useState(false)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-tactical-surface border border-tactical-border rounded-lg max-w-md w-full">
        <div className="px-6 py-4 border-b border-tactical-border flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Mic className="w-5 h-5 text-tactical-primary" />
            <h2 className="text-lg font-bold text-tactical-primary font-mono">
              VOICE DEBRIEF
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
          <div className="text-center py-8">
            <button
              onClick={() => setIsRecording(!isRecording)}
              className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4 transition-all ${
                isRecording
                  ? 'bg-threat-high text-white animate-pulse'
                  : 'bg-tactical-primary text-black hover:bg-opacity-90'
              }`}
            >
              {isRecording ? (
                <MicOff className="w-12 h-12" />
              ) : (
                <Mic className="w-12 h-12" />
              )}
            </button>
            <p className="text-tactical-muted text-sm">
              {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
            </p>
          </div>
          <div className="alert-info">
            <p className="text-sm">
              Voice debriefing feature will be available soon. Record your observations
              and the AI will automatically structure them into a formal SITREP.
            </p>
          </div>
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

export default SitrepPanel
