"""
WebSocket API Routes
Real-time data streaming for threats, tracking, and tactical updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set
import logging
import json
import asyncio
from datetime import datetime

from app.database.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Store active connections by channel
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "threats": set(),
            "tracking": set(),
            "sitrep": set(),
            "tactical": set(),
            "all": set()
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        """Accept new WebSocket connection"""
        await websocket.accept()

        if channel not in self.active_connections:
            self.active_connections[channel] = set()

        self.active_connections[channel].add(websocket)
        self.active_connections["all"].add(websocket)

        logger.info(f"Client connected to channel: {channel}. Total: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        """Remove WebSocket connection"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

        self.active_connections["all"].discard(websocket)

        logger.info(f"Client disconnected from channel: {channel}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")

    async def broadcast(self, message: dict, channel: str = "all"):
        """Broadcast message to all clients on channel"""
        if channel not in self.active_connections:
            return

        disconnected = set()

        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, channel)

    async def broadcast_threat_update(self, threat_data: dict):
        """Broadcast threat update"""
        message = {
            "type": "threat_update",
            "data": threat_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message, "threats")
        await self.broadcast(message, "tactical")

    async def broadcast_tracking_update(self, tracking_data: dict):
        """Broadcast tracking update"""
        message = {
            "type": "tracking_update",
            "data": tracking_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message, "tracking")
        await self.broadcast(message, "tactical")

    async def broadcast_sitrep_update(self, sitrep_data: dict):
        """Broadcast SITREP update"""
        message = {
            "type": "sitrep_update",
            "data": sitrep_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message, "sitrep")
        await self.broadcast(message, "tactical")

    async def broadcast_tactical_update(self, tactical_data: dict):
        """Broadcast tactical picture update"""
        message = {
            "type": "tactical_update",
            "data": tactical_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message, "tactical")

    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            channel: len(connections)
            for channel, connections in self.active_connections.items()
        }


# Create global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, channel: str = "all"):
    """
    Main WebSocket endpoint

    Channels:
    - all: All updates
    - threats: Threat detections only
    - tracking: GPS tracking updates only
    - sitrep: SITREP updates only
    - tactical: Tactical picture updates only

    Message Format:
    {
        "type": "threat_update" | "tracking_update" | "sitrep_update" | "tactical_update",
        "data": { ... },
        "timestamp": "ISO-8601 timestamp"
    }
    """
    await manager.connect(websocket, channel)

    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "message": f"Connected to Tactical AEGIS - Channel: {channel}",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)

                elif message.get("type") == "subscribe":
                    # Subscribe to additional channel
                    new_channel = message.get("channel")
                    if new_channel in manager.active_connections:
                        manager.active_connections[new_channel].add(websocket)
                        await manager.send_personal_message({
                            "type": "subscribed",
                            "channel": new_channel,
                            "timestamp": datetime.utcnow().isoformat()
                        }, websocket)

                elif message.get("type") == "unsubscribe":
                    # Unsubscribe from channel
                    old_channel = message.get("channel")
                    if old_channel in manager.active_connections:
                        manager.active_connections[old_channel].discard(websocket)
                        await manager.send_personal_message({
                            "type": "unsubscribed",
                            "channel": old_channel,
                            "timestamp": datetime.utcnow().isoformat()
                        }, websocket)

                elif message.get("type") == "get_stats":
                    # Send connection statistics
                    await manager.send_personal_message({
                        "type": "stats",
                        "data": manager.get_stats(),
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)

            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info(f"Client disconnected from {channel}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket, channel)


@router.websocket("/ws/threats")
async def websocket_threats(websocket: WebSocket):
    """WebSocket endpoint for threat updates only"""
    await websocket_endpoint(websocket, channel="threats")


@router.websocket("/ws/tracking")
async def websocket_tracking(websocket: WebSocket):
    """WebSocket endpoint for tracking updates only"""
    await websocket_endpoint(websocket, channel="tracking")


@router.websocket("/ws/sitrep")
async def websocket_sitrep(websocket: WebSocket):
    """WebSocket endpoint for SITREP updates only"""
    await websocket_endpoint(websocket, channel="sitrep")


@router.websocket("/ws/tactical")
async def websocket_tactical(websocket: WebSocket):
    """WebSocket endpoint for tactical picture updates"""
    await websocket_endpoint(websocket, channel="tactical")


# Helper functions for broadcasting from other parts of the application

async def broadcast_new_threat(threat_data: dict):
    """Broadcast new threat detection"""
    await manager.broadcast_threat_update(threat_data)


async def broadcast_position_update(unit_data: dict):
    """Broadcast unit position update"""
    await manager.broadcast_tracking_update(unit_data)


async def broadcast_new_sitrep(sitrep_data: dict):
    """Broadcast new SITREP"""
    await manager.broadcast_sitrep_update(sitrep_data)


async def broadcast_tactical_picture(tactical_data: dict):
    """Broadcast tactical picture update"""
    await manager.broadcast_tactical_update(tactical_data)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager"""
    return manager
