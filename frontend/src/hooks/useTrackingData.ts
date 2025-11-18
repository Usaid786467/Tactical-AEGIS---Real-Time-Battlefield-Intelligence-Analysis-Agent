/**
 * Tracking Data Hook
 * React hook for managing friendly force tracking with real-time updates
 */

import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { useWebSocket } from './useWebSocket'
import type { FriendlyForce, FriendlyForceCreate, FriendlyForceUpdate } from '@/types'

export function useTrackingData() {
  const queryClient = useQueryClient()
  const [units, setUnits] = useState<FriendlyForce[]>([])

  // Fetch units
  const {
    data: fetchedUnits,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['units'],
    queryFn: () => apiClient.getUnits({ active_only: true }),
  })

  // Update local state when data changes
  useEffect(() => {
    if (fetchedUnits) {
      setUnits(fetchedUnits)
    }
  }, [fetchedUnits])

  // Real-time tracking updates
  useWebSocket({
    channel: 'tracking',
    onMessage: (message) => {
      if (message.type === 'tracking_update') {
        // Update specific unit or refetch all
        queryClient.invalidateQueries({ queryKey: ['units'] })
      }
    },
  })

  // Create unit mutation
  const createUnitMutation = useMutation({
    mutationFn: (unit: FriendlyForceCreate) => apiClient.createUnit(unit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['units'] })
    },
  })

  // Update unit mutation
  const updateUnitMutation = useMutation({
    mutationFn: ({ unitId, update }: { unitId: string; update: FriendlyForceUpdate }) =>
      apiClient.updateUnitPosition(unitId, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['units'] })
    },
  })

  // Delete unit mutation
  const deleteUnitMutation = useMutation({
    mutationFn: (unitId: string) => apiClient.deleteUnit(unitId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['units'] })
    },
  })

  return {
    units,
    isLoading,
    error,
    refetch,
    createUnit: createUnitMutation.mutate,
    updateUnit: updateUnitMutation.mutate,
    deleteUnit: deleteUnitMutation.mutate,
    isCreating: createUnitMutation.isPending,
    isUpdating: updateUnitMutation.isPending,
    isDeleting: deleteUnitMutation.isPending,
  }
}

export default useTrackingData
