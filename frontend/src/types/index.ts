/**
 * Central type exports
 */

export * from './threat'
export * from './sitrep'
export * from './tracking'

// Common types
export interface TacticalPicture {
  timestamp: string
  area_bounds?: {
    north: number
    south: number
    east: number
    west: number
  }
  threats: {
    total: number
    by_type: Record<string, number>
    by_level: Record<string, number>
    data: any[]
  }
  friendly_forces: {
    total: number
    by_status: Record<string, number>
    data: any[]
  }
  situation_assessment: {
    status: string
    summary: string
    threat_count: number
    units_at_risk: number
    avg_threat_level: number
  }
  recommendations: string[]
}

export interface WebSocketMessage {
  type: 'threat_update' | 'tracking_update' | 'sitrep_update' | 'tactical_update' | 'connection' | 'pong' | 'error'
  data?: any
  message?: string
  timestamp: string
}
