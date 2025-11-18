/**
 * SITREP-related type definitions
 */

export enum SitrepPriority {
  ROUTINE = 'routine',
  PRIORITY = 'priority',
  IMMEDIATE = 'immediate',
  FLASH = 'flash',
}

export enum SitrepClassification {
  UNCLASSIFIED = 'unclassified',
  CONFIDENTIAL = 'confidential',
  SECRET = 'secret',
  TOP_SECRET = 'top_secret',
}

export enum SitrepSource {
  VOICE = 'voice',
  MANUAL = 'manual',
  AUTO = 'auto',
}

export interface Entity {
  type: string
  value: string
  confidence: number
}

export interface Sitrep {
  id: number
  title: string
  report_time: string
  location?: string
  latitude?: number
  longitude?: number
  unit?: string
  reporter?: string

  // SITREP sections
  situation?: string
  mission?: string
  execution?: string
  admin_logistics?: string
  command_signal?: string

  // Extracted data
  entities?: Entity[]
  source: string
  audio_transcript?: string
  metadata?: Record<string, any>

  priority: SitrepPriority
  classification: SitrepClassification

  created_at: string
  updated_at: string
}

export interface SitrepCreate {
  title: string
  location?: string
  latitude?: number
  longitude?: number
  unit?: string
  reporter?: string
  situation?: string
  mission?: string
  execution?: string
  admin_logistics?: string
  command_signal?: string
  priority?: SitrepPriority
  classification?: SitrepClassification
  source?: SitrepSource
  audio_transcript?: string
}

export interface SitrepUpdate {
  title?: string
  situation?: string
  mission?: string
  execution?: string
  admin_logistics?: string
  command_signal?: string
  priority?: SitrepPriority
}

export interface VoiceDebriefingRequest {
  audio_data: string
  audio_format?: string
  reporter?: string
  location?: string
}

export interface VoiceDebriefingResponse {
  sitrep: Sitrep
  transcript: string
  entities: Entity[]
  processing_time: number
  confidence: number
}

export interface SitrepGenerationRequest {
  text_input: string
  include_entities?: boolean
  auto_classify?: boolean
}

export interface SitrepGenerationResponse {
  sitrep: Sitrep
  entities: Entity[]
  processing_time: number
}
