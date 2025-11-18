/**
 * Threat Data Hook
 * React hook for managing threat data with real-time updates
 */

import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { useWebSocket } from './useWebSocket'
import type { Threat, ThreatCreate, ThreatUpdate } from '@/types'

export function useThreatData() {
  const queryClient = useQueryClient()
  const [threats, setThreats] = useState<Threat[]>([])

  // Fetch threats
  const {
    data: fetchedThreats,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['threats'],
    queryFn: () => apiClient.getThreats({ active_only: true }),
  })

  // Update local state when data changes
  useEffect(() => {
    if (fetchedThreats) {
      setThreats(fetchedThreats)
    }
  }, [fetchedThreats])

  // Real-time updates
  useWebSocket({
    channel: 'threats',
    onMessage: (message) => {
      if (message.type === 'threat_update') {
        // Invalidate and refetch
        queryClient.invalidateQueries({ queryKey: ['threats'] })
      }
    },
  })

  // Create threat mutation
  const createThreatMutation = useMutation({
    mutationFn: (threat: ThreatCreate) => apiClient.createThreat(threat),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threats'] })
    },
  })

  // Update threat mutation
  const updateThreatMutation = useMutation({
    mutationFn: ({ id, update }: { id: number; update: ThreatUpdate }) =>
      apiClient.updateThreat(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threats'] })
    },
  })

  // Delete threat mutation
  const deleteThreatMutation = useMutation({
    mutationFn: (id: number) => apiClient.deleteThreat(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threats'] })
    },
  })

  return {
    threats,
    isLoading,
    error,
    refetch,
    createThreat: createThreatMutation.mutate,
    updateThreat: updateThreatMutation.mutate,
    deleteThreat: deleteThreatMutation.mutate,
    isCreating: createThreatMutation.isPending,
    isUpdating: updateThreatMutation.isPending,
    isDeleting: deleteThreatMutation.isPending,
  }
}

export default useThreatData
