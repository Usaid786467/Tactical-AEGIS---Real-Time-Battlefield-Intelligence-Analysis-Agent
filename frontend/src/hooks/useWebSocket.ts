/**
 * WebSocket Hook
 * React hook for WebSocket connections
 */

import { useEffect, useState, useCallback, useRef } from 'react'
import { WebSocketClient } from '@/services/websocket'
import type { WebSocketMessage } from '@/types'

interface UseWebSocketOptions {
  channel?: string
  autoConnect?: boolean
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    channel = 'all',
    autoConnect = true,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocketClient | null>(null)

  useEffect(() => {
    // Create WebSocket client
    wsRef.current = new WebSocketClient(channel)

    // Setup connection handler
    const unsubConnect = wsRef.current.onConnect(() => {
      setIsConnected(true)
      onConnect?.()
    })

    // Setup disconnection handler
    const unsubDisconnect = wsRef.current.onDisconnect(() => {
      setIsConnected(false)
      onDisconnect?.()
    })

    // Setup error handler
    const unsubError = wsRef.current.onError((error) => {
      onError?.(error)
    })

    // Setup message handler for all messages
    const unsubMessage = wsRef.current.on('*', (message) => {
      setLastMessage(message)
      onMessage?.(message)
    })

    // Auto-connect if enabled
    if (autoConnect) {
      wsRef.current.connect()
    }

    // Cleanup
    return () => {
      unsubConnect()
      unsubDisconnect()
      unsubError()
      unsubMessage()
      wsRef.current?.disconnect()
    }
  }, [channel, autoConnect])

  const send = useCallback((message: Record<string, any>) => {
    wsRef.current?.send(message)
  }, [])

  const subscribe = useCallback((messageType: string, handler: (message: WebSocketMessage) => void) => {
    return wsRef.current?.on(messageType, handler) || (() => {})
  }, [])

  const connect = useCallback(() => {
    wsRef.current?.connect()
  }, [])

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect()
  }, [])

  return {
    isConnected,
    lastMessage,
    send,
    subscribe,
    connect,
    disconnect,
  }
}

export default useWebSocket
