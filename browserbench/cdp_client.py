"""CDP Client Functions"""

import base64
import json
import os
import socket
import struct
from urllib.parse import urlparse


class CDPClient:
    """Minimal Chrome DevTools Protocol WebSocket client (stdlib only)."""

    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.sock = None
        self.message_id = 0

    def connect(self):
        """Trying to connect to the webpage to control it"""
        parsed = urlparse(self.websocket_url)
        host = parsed.hostname
        port = parsed.port
        path = parsed.path

        self.sock = socket.create_connection((host, port))

        key = base64.b64encode(os.urandom(16)).decode()

        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )

        self.sock.send(handshake.encode())
        self.sock.recv(4096)

    def _send_frame(self, payload: str):
        payload_bytes = payload.encode()
        frame = bytearray([0x81])  # FIN + text frame

        length = len(payload_bytes)
        if length < 126:
            frame.append(0x80 | length)
        elif length < 65536:
            frame.append(0x80 | 126)
            frame.extend(struct.pack(">H", length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack(">Q", length))

        mask = os.urandom(4)
        frame.extend(mask)

        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload_bytes))
        frame.extend(masked)

        self.sock.send(frame)

    def _recv_frame(self) -> str:
        header = self.sock.recv(2)
        length = header[1] & 0x7F

        if length == 126:
            length = struct.unpack(">H", self.sock.recv(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self.sock.recv(8))[0]

        return self.sock.recv(length).decode()

    def call(self, method: str, params: dict | None = None) -> dict:
        """Sends a CDP command and waits for a response"""
        self.message_id += 1
        message = {"id": self.message_id, "method": method, "params": params or {}}
        self._send_frame(json.dumps(message))

        while True:
            response = json.loads(self._recv_frame())
            if response.get("id") == self.message_id:
                return response
