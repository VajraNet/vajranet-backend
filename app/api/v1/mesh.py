"""
VajraNet P2P Mesh WebSocket Relay
Enables real device-to-device LAN mesh communication via the backend as a relay.
Devices connect via WebSocket and can discover peers, send/receive messages,
broadcast SOS, and announce GPS presence — all through the backend relay.
"""

import json
import asyncio
import logging
from typing import Dict, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mesh", tags=["P2P Mesh WebSocket Relay"])

# In-memory peer registry: device_id -> {websocket, name, role, lat, lon, last_seen}
_peers: Dict[str, dict] = {}


def _get_peer_list(exclude_id: Optional[str] = None) -> list:
    """Return serializable list of connected peers."""
    now = datetime.utcnow().isoformat()
    return [
        {
            "id": pid,
            "name": info["name"],
            "role": info["role"],
            "lat": info.get("lat"),
            "lon": info.get("lon"),
            "last_seen": info.get("last_seen", now),
            "hops": 1,
            "is_verified": False,
        }
        for pid, info in _peers.items()
        if pid != exclude_id
    ]


async def _broadcast(sender_id: str, payload: dict):
    """Send a message to all connected peers except the sender."""
    disconnected = []
    for peer_id, peer_info in list(_peers.items()):
        if peer_id == sender_id:
            continue
        try:
            await peer_info["ws"].send_text(json.dumps(payload))
        except Exception:
            disconnected.append(peer_id)

    for pid in disconnected:
        _peers.pop(pid, None)


async def _send_to(target_id: str, payload: dict):
    """Send a message to a specific peer."""
    peer_info = _peers.get(target_id)
    if peer_info:
        try:
            await peer_info["ws"].send_text(json.dumps(payload))
        except Exception:
            _peers.pop(target_id, None)


@router.websocket("/ws/{device_id}")
async def mesh_websocket(websocket: WebSocket, device_id: str):
    """
    WebSocket endpoint for VajraNet P2P Mesh Relay.

    Protocol (JSON messages):
      CLIENT -> SERVER:
        { "type": "JOIN", "name": "...", "role": "...", "lat": 0.0, "lon": 0.0 }
        { "type": "MESSAGE", "target_id": "...", "text": "..." }     # DM
        { "type": "BROADCAST", "text": "..." }                       # To all peers
        { "type": "SOS", "lat": 0.0, "lon": 0.0, "severity": "..." }
        { "type": "PING" }                                            # Keepalive
        { "type": "LOCATION", "lat": 0.0, "lon": 0.0 }

      SERVER -> CLIENT:
        { "type": "PEER_LIST", "peers": [...] }                      # On join
        { "type": "PEER_JOINED", "peer": {...} }                      # Announce new peer
        { "type": "PEER_LEFT", "device_id": "..." }                   # Peer disconnected
        { "type": "MESSAGE", "from_id": "...", "from_name": "...", "text": "...", "time": "..." }
        { "type": "BROADCAST", "from_id": "...", "from_name": "...", "text": "...", "time": "..." }
        { "type": "SOS", "from_id": "...", "from_name": "...", "lat": ..., "lon": ..., "severity": "..." }
        { "type": "PONG" }
    """
    await websocket.accept()
    logger.info(f"[MeshRelay] Device {device_id} connected")

    # Register this peer
    _peers[device_id] = {
        "ws": websocket,
        "name": device_id,
        "role": "Citizen",
        "lat": None,
        "lon": None,
        "last_seen": datetime.utcnow().isoformat(),
    }

    # Send current peer list to the newly joined device
    await websocket.send_text(json.dumps({
        "type": "PEER_LIST",
        "peers": _get_peer_list(exclude_id=device_id),
        "your_id": device_id,
    }))

    # Announce this new peer to all others
    await _broadcast(device_id, {
        "type": "PEER_JOINED",
        "peer": {
            "id": device_id,
            "name": _peers[device_id]["name"],
            "role": _peers[device_id]["role"],
            "lat": None,
            "lon": None,
            "hops": 1,
            "is_verified": False,
        },
    })

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            mtype = msg.get("type", "").upper()
            now = datetime.utcnow().isoformat()

            if mtype == "JOIN":
                # Update peer metadata
                _peers[device_id]["name"] = msg.get("name", device_id)
                _peers[device_id]["role"] = msg.get("role", "Citizen")
                _peers[device_id]["lat"] = msg.get("lat")
                _peers[device_id]["lon"] = msg.get("lon")
                _peers[device_id]["last_seen"] = now

                # Announce updated info to all peers
                await _broadcast(device_id, {
                    "type": "PEER_JOINED",
                    "peer": {
                        "id": device_id,
                        "name": _peers[device_id]["name"],
                        "role": _peers[device_id]["role"],
                        "lat": _peers[device_id]["lat"],
                        "lon": _peers[device_id]["lon"],
                        "hops": 1,
                        "is_verified": False,
                    },
                })

                # Send updated peer list back
                await websocket.send_text(json.dumps({
                    "type": "PEER_LIST",
                    "peers": _get_peer_list(exclude_id=device_id),
                }))

            elif mtype == "MESSAGE":
                target_id = msg.get("target_id")
                text = msg.get("text", "")
                sender = _peers.get(device_id, {})
                payload = {
                    "type": "MESSAGE",
                    "from_id": device_id,
                    "from_name": sender.get("name", device_id),
                    "text": text,
                    "time": now,
                }
                if target_id:
                    await _send_to(target_id, payload)
                else:
                    await _broadcast(device_id, payload)

            elif mtype == "BROADCAST":
                text = msg.get("text", "")
                sender = _peers.get(device_id, {})
                await _broadcast(device_id, {
                    "type": "BROADCAST",
                    "from_id": device_id,
                    "from_name": sender.get("name", device_id),
                    "text": text,
                    "time": now,
                })

            elif mtype == "SOS":
                sender = _peers.get(device_id, {})
                await _broadcast(device_id, {
                    "type": "SOS",
                    "from_id": device_id,
                    "from_name": sender.get("name", device_id),
                    "lat": msg.get("lat"),
                    "lon": msg.get("lon"),
                    "severity": msg.get("severity", "CRITICAL"),
                    "time": now,
                })

            elif mtype == "LOCATION":
                _peers[device_id]["lat"] = msg.get("lat")
                _peers[device_id]["lon"] = msg.get("lon")
                _peers[device_id]["last_seen"] = now

            elif mtype == "PING":
                _peers[device_id]["last_seen"] = now
                await websocket.send_text(json.dumps({"type": "PONG"}))

    except WebSocketDisconnect:
        logger.info(f"[MeshRelay] Device {device_id} disconnected")
    except Exception as e:
        logger.warning(f"[MeshRelay] Device {device_id} error: {e}")
    finally:
        _peers.pop(device_id, None)
        # Notify all remaining peers of departure
        await _broadcast(device_id, {
            "type": "PEER_LEFT",
            "device_id": device_id,
        })
