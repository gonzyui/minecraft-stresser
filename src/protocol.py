"""
Minecraft Protocol Implementation
Handles Minecraft protocol packets and connections
"""
import struct
import hashlib
import socket
import asyncio
from typing import Optional, Tuple


class MinecraftProtocol:
    """Minecraft protocol handler for version 1.21.1 (protocol 767)"""

    PROTOCOL_VERSION = 767

    @staticmethod
    def pack_varint(val: int) -> bytes:
        """Pack integer into VarInt format"""
        out = b''
        while True:
            byte = val & 0x7F
            val >>= 7
            if val:
                out += bytes([byte | 0x80])
            else:
                out += bytes([byte])
                break
        return out

    @staticmethod
    def pack_string(s: str) -> bytes:
        """Pack string with length prefix"""
        encoded = s.encode('utf-8')
        return MinecraftProtocol.pack_varint(len(encoded)) + encoded

    @staticmethod
    def get_offline_uuid(username: str) -> bytes:
        """Generate offline UUID for Minecraft"""
        data = "OfflinePlayer:" + username
        digest = bytearray(hashlib.md5(data.encode('utf-8')).digest())
        digest[6] = digest[6] & 0x0f | 0x30
        digest[8] = digest[8] & 0x3f | 0x80
        return bytes(digest)

    @staticmethod
    def create_handshake_packet(ip: str, port: int, next_state: int) -> bytes:
        """Create a Minecraft handshake packet"""
        handshake = (
            MinecraftProtocol.pack_varint(0x00) +
            MinecraftProtocol.pack_varint(MinecraftProtocol.PROTOCOL_VERSION) +
            MinecraftProtocol.pack_string(ip) +
            struct.pack('>H', port) +
            MinecraftProtocol.pack_varint(next_state)
        )
        return MinecraftProtocol.pack_varint(len(handshake)) + handshake

    @staticmethod
    def create_status_request_packet() -> bytes:
        """Create a status request packet"""
        request = MinecraftProtocol.pack_varint(0x00)
        return MinecraftProtocol.pack_varint(len(request)) + request

    @staticmethod
    def create_login_start_packet(username: str) -> bytes:
        """Create a login start packet"""
        login_start = (
            MinecraftProtocol.pack_varint(0x00) +
            MinecraftProtocol.pack_string(username) +
            MinecraftProtocol.get_offline_uuid(username)
        )
        return MinecraftProtocol.pack_varint(len(login_start)) + login_start

    @staticmethod
    async def perform_handshake(sock: socket.socket, ip: str, port: int, next_state: int) -> bool:
        """Perform Minecraft handshake"""
        try:
            handshake_packet = MinecraftProtocol.create_handshake_packet(ip, port, next_state)
            await asyncio.get_running_loop().sock_sendall(sock, handshake_packet)
            return True
        except Exception:
            return False

    @staticmethod
    async def perform_status_request(sock: socket.socket) -> bool:
        """Perform status request"""
        try:
            status_packet = MinecraftProtocol.create_status_request_packet()
            await asyncio.get_running_loop().sock_sendall(sock, status_packet)
            return True
        except Exception:
            return False

    @staticmethod
    async def perform_login_start(sock: socket.socket, username: str) -> bool:
        """Perform login start"""
        try:
            login_packet = MinecraftProtocol.create_login_start_packet(username)
            await asyncio.get_running_loop().sock_sendall(sock, login_packet)
            return True
        except Exception:
            return False