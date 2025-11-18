/**
 * API Client
 * Handles all HTTP requests to the backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  Threat,
  ThreatCreate,
  ThreatUpdate,
  ThreatAnalysisRequest,
  ThreatPredictionRequest,
  ThreatPredictionResponse,
  Sitrep,
  SitrepCreate,
  SitrepUpdate,
  VoiceDebriefingRequest,
  VoiceDebriefingResponse,
  SitrepGenerationRequest,
  SitrepGenerationResponse,
  FriendlyForce,
  FriendlyForceCreate,
  FriendlyForceUpdate,
  TrackingUpdate,
  BlueonBlueCheck,
  BlueonBlueResponse,
  DeploymentOptimization,
  TacticalPicture,
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('auth_token')
          // Redirect to login or refresh token
        }
        return Promise.reject(error)
      }
    )
  }

  // Threat Analysis API
  async analyzeImage(request: ThreatAnalysisRequest) {
    const response = await this.client.post('/api/threats/analyze/image', request)
    return response.data
  }

  async predictThreats(request: ThreatPredictionRequest): Promise<ThreatPredictionResponse> {
    const response = await this.client.post('/api/threats/predict', request)
    return response.data
  }

  async getThreats(params?: {
    skip?: number
    limit?: number
    active_only?: boolean
    threat_level?: string
    threat_type?: string
  }): Promise<Threat[]> {
    const response = await this.client.get('/api/threats', { params })
    return response.data
  }

  async getThreat(id: number): Promise<Threat> {
    const response = await this.client.get(`/api/threats/${id}`)
    return response.data
  }

  async createThreat(threat: ThreatCreate): Promise<Threat> {
    const response = await this.client.post('/api/threats', threat)
    return response.data
  }

  async updateThreat(id: number, update: ThreatUpdate): Promise<Threat> {
    const response = await this.client.patch(`/api/threats/${id}`, update)
    return response.data
  }

  async deleteThreat(id: number): Promise<void> {
    await this.client.delete(`/api/threats/${id}`)
  }

  // SITREP API
  async generateSitrep(request: SitrepGenerationRequest): Promise<SitrepGenerationResponse> {
    const response = await this.client.post('/api/sitrep/generate', request)
    return response.data
  }

  async voiceDebrief(request: VoiceDebriefingRequest): Promise<VoiceDebriefingResponse> {
    const response = await this.client.post('/api/sitrep/voice-debrief', request)
    return response.data
  }

  async getSitreps(params?: {
    skip?: number
    limit?: number
    priority?: string
    source?: string
  }): Promise<Sitrep[]> {
    const response = await this.client.get('/api/sitrep/sitreps', { params })
    return response.data
  }

  async getSitrep(id: number): Promise<Sitrep> {
    const response = await this.client.get(`/api/sitrep/sitreps/${id}`)
    return response.data
  }

  async createSitrep(sitrep: SitrepCreate): Promise<Sitrep> {
    const response = await this.client.post('/api/sitrep/sitreps', sitrep)
    return response.data
  }

  async updateSitrep(id: number, update: SitrepUpdate): Promise<Sitrep> {
    const response = await this.client.patch(`/api/sitrep/sitreps/${id}`, update)
    return response.data
  }

  async deleteSitrep(id: number): Promise<void> {
    await this.client.delete(`/api/sitrep/sitreps/${id}`)
  }

  // Tracking API
  async createUnit(unit: FriendlyForceCreate): Promise<FriendlyForce> {
    const response = await this.client.post('/api/tracking/units', unit)
    return response.data
  }

  async getUnits(params?: {
    skip?: number
    limit?: number
    active_only?: boolean
    status?: string
    unit_type?: string
  }): Promise<FriendlyForce[]> {
    const response = await this.client.get('/api/tracking/units', { params })
    return response.data
  }

  async getUnit(unitId: string): Promise<FriendlyForce> {
    const response = await this.client.get(`/api/tracking/units/${unitId}`)
    return response.data
  }

  async updateUnitPosition(unitId: string, update: FriendlyForceUpdate): Promise<FriendlyForce> {
    const response = await this.client.patch(`/api/tracking/units/${unitId}`, update)
    return response.data
  }

  async trackingUpdate(update: TrackingUpdate): Promise<void> {
    await this.client.post('/api/tracking/tracking/update', update)
  }

  async checkBlueOnBlue(check: BlueonBlueCheck): Promise<BlueonBlueResponse> {
    const response = await this.client.post('/api/tracking/blue-on-blue/check', check)
    return response.data
  }

  async getProximityAlerts(threshold_meters?: number) {
    const response = await this.client.get('/api/tracking/proximity-alerts', {
      params: { threshold_meters },
    })
    return response.data
  }

  async optimizeDeployment(request: DeploymentOptimization) {
    const response = await this.client.post('/api/tracking/deployment/optimize', request)
    return response.data
  }

  async getNearbyUnits(latitude: number, longitude: number, radius_km?: number) {
    const response = await this.client.get('/api/tracking/nearby', {
      params: { latitude, longitude, radius_km },
    })
    return response.data
  }

  async deleteUnit(unitId: string): Promise<void> {
    await this.client.delete(`/api/tracking/units/${unitId}`)
  }

  // Data Fusion API
  async getTacticalPicture(bounds?: {
    north?: number
    south?: number
    east?: number
    west?: number
  }): Promise<TacticalPicture> {
    const response = await this.client.get('/api/fusion/tactical-picture', {
      params: bounds,
    })
    return response.data
  }

  async fuseThreats(correlation_radius_km?: number, time_window_hours?: number) {
    const response = await this.client.post('/api/fusion/fuse-threats', null, {
      params: { correlation_radius_km, time_window_hours },
    })
    return response.data
  }

  async getSituationAssessment(bounds?: {
    north?: number
    south?: number
    east?: number
    west?: number
  }) {
    const response = await this.client.get('/api/fusion/situation-assessment', {
      params: bounds,
    })
    return response.data
  }

  async getThreatDistribution() {
    const response = await this.client.get('/api/fusion/threat-distribution')
    return response.data
  }

  async getForceDisposition() {
    const response = await this.client.get('/api/fusion/force-disposition')
    return response.data
  }

  async getIntelligenceSummary(hours?: number) {
    const response = await this.client.get('/api/fusion/intelligence-summary', {
      params: { hours },
    })
    return response.data
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health')
    return response.data
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
export default apiClient
