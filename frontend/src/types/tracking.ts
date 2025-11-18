/**
 * Tracking-related type definitions
 */

export enum UnitType {
  INFANTRY = 'infantry',
  ARMOR = 'armor',
  AVIATION = 'aviation',
  ARTILLERY = 'artillery',
  LOGISTICS = 'logistics',
  COMMAND = 'command',
  SPECIAL_FORCES = 'special_forces',
  OTHER = 'other',
}

export enum UnitStatus {
  GREEN = 'green',
  AMBER = 'amber',
  RED = 'red',
  BLACK = 'black',
}

export interface FriendlyForce {
  id: number
  unit_id: string
  unit_name: string
  unit_type?: UnitType
  callsign?: string

  // Position
  latitude: number
  longitude: number
  altitude?: number
  heading?: number
  speed?: number

  // Status
  status: UnitStatus
  personnel_count?: number
  equipment?: Record<string, any>

  // Metadata
  last_contact: string
  metadata?: Record<string, any>
  active: boolean
  created_at: string
  updated_at: string
}

export interface FriendlyForceCreate {
  unit_id: string
  unit_name: string
  unit_type?: UnitType
  callsign?: string
  latitude: number
  longitude: number
  altitude?: number
  heading?: number
  speed?: number
  status?: UnitStatus
  personnel_count?: number
  equipment?: Record<string, any>
}

export interface FriendlyForceUpdate {
  latitude?: number
  longitude?: number
  altitude?: number
  heading?: number
  speed?: number
  status?: UnitStatus
  personnel_count?: number
  equipment?: Record<string, any>
}

export interface TrackingUpdate {
  unit_id: string
  latitude: number
  longitude: number
  timestamp: string
  heading?: number
  speed?: number
}

export interface ProximityAlert {
  alert_type: string
  unit1_id: string
  unit2_id: string
  distance: number
  time_to_closest?: number
  severity: string
  message: string
}

export interface BlueonBlueCheck {
  target_latitude: number
  target_longitude: number
  radius?: number
}

export interface BlueonBlueResponse {
  safe: boolean
  nearby_units: Array<{
    unit_id: string
    unit_name: string
    callsign?: string
    distance_meters: number
    latitude: number
    longitude: number
    status: UnitStatus
  }>
  minimum_distance?: number
  alerts: ProximityAlert[]
}

export interface DeploymentOptimization {
  available_units: string[]
  objective_location: {
    latitude: number
    longitude: number
  }
  mission_type: string
  time_critical?: boolean
}

export interface DeploymentRecommendation {
  unit_id: string
  unit_name: string
  callsign?: string
  current_position: {
    latitude: number
    longitude: number
  }
  distance_km: number
  estimated_time_hours: number
  bearing: number
  recommended_route: Array<{ latitude: number; longitude: number }>
  priority: number
  reasoning: string
}
