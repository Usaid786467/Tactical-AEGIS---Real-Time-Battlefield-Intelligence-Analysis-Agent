/**
 * Threat-related type definitions
 */

export enum ThreatLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum ThreatType {
  VEHICLE = 'vehicle',
  PERSONNEL = 'personnel',
  WEAPON = 'weapon',
  IED = 'ied',
  ARTILLERY = 'artillery',
  AIRCRAFT = 'aircraft',
  UNKNOWN = 'unknown',
}

export enum ThreatSource {
  SATELLITE = 'satellite',
  DRONE = 'drone',
  SENSOR = 'sensor',
  RADIO = 'radio',
  MANUAL = 'manual',
}

export interface Threat {
  id: number
  threat_type: ThreatType
  threat_level: ThreatLevel
  confidence: number
  latitude: number
  longitude: number
  grid_reference?: string
  description?: string
  source: ThreatSource
  metadata?: Record<string, any>
  image_url?: string
  detected_at: string
  verified: boolean
  active: boolean
  created_at: string
  updated_at: string
}

export interface ThreatCreate {
  threat_type: ThreatType
  threat_level: ThreatLevel
  confidence: number
  latitude: number
  longitude: number
  grid_reference?: string
  description?: string
  source: ThreatSource
  metadata?: Record<string, any>
  image_url?: string
}

export interface ThreatUpdate {
  threat_level?: ThreatLevel
  verified?: boolean
  active?: boolean
  description?: string
  metadata?: Record<string, any>
}

export interface ThreatAnalysisRequest {
  image_data?: string
  image_url?: string
  text_data?: string
  audio_data?: string
  latitude?: number
  longitude?: number
  source: ThreatSource
}

export interface PredictedThreat {
  threat_type: ThreatType
  latitude: number
  longitude: number
  probability: number
  confidence: number
  reasoning: string
  predicted_time?: string
}

export interface ThreatPredictionRequest {
  area_bounds: {
    north: number
    south: number
    east: number
    west: number
  }
  time_horizon_hours?: number
  historical_days?: number
  threat_types?: ThreatType[]
}

export interface ThreatPredictionResponse {
  predictions: PredictedThreat[]
  analysis_time: number
  model_version: string
  factors_considered: string[]
}
