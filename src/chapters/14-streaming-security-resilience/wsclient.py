# wsclient.py -- a minimal WebSocket client (RFC 6455) for the Pico
#
# MicroPython's built-in `websocket` module does NOT mask the frames it sends,
# and the standard says a client must, so a correct server (including the
# `websockets` package the buddy server uses) closes the connection. This module
# does the handshake and the framing itself, in about 100 lines:
#
#   ws = WebSocket.connect(host, port, "/v1/stream", {"X-Buddy-Token": "..."})
#   ws.send_text('{"event": "start"}')
#   ws.send_binary(view)               # a chunk of audio
#   kind, payload = ws.recv()          # ("text", str) | ("binary", bytes)
#   ws.close()
#
# Limits, on purpose: no fragmented messages, no frames over 65,535 bytes, no
# extensions. It answers pings with pongs, and raises WsClosed when the server
# closes. UNTESTED ON THE KIT (the book's author tested it against a real
# server on a computer, with a fake Pico layer): the masking trick below is
# the first thing to check on the device.

import binascii
import hashlib
import os

import buddy_http

GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"       # fixed by the standard
TEXT, BINARY, CLOSE, PING, PONG = 0x1, 0x2, 0x8, 0x9, 0xA
MAX_FRAME = 4096                                     # refuse bigger incoming frames


class WsClosed(Exception):
    retryable = True


def _xor_mask(data, key):
    """data XOR key repeated, using big-number arithmetic (done in C, no Python loop)."""
    n = len(data)
    if n == 0:
        return b""
    repeated = (key * (n // 4 + 1))[:n]
    return (int.from_bytes(data, "big") ^ int.from_bytes(repeated, "big")).to_bytes(n, "big")


def _read_exact(sock, n):
    data = b""
    while len(data) < n:
        more = sock.read(n - len(data)) if hasattr(sock, "read") else sock.recv(n - len(data))
        if not more:
            raise WsClosed("connection closed")
        data += more
    return data


def _write(sock, data):
    view = memoryview(data)
    while len(view):
        n = sock.write(view) if hasattr(sock, "write") else sock.send(view)
        view = view[n:]


class WebSocket:
    def __init__(self, sock):
        self.sock = sock
        self.open = True

    @classmethod
    def connect(cls, host, port, path, headers=None, timeout_s=8, tls=False, cadata=None):
        sock = buddy_http.open_socket(host, port, timeout_s, tls, cadata)
        try:
            key = binascii.b2a_base64(os.urandom(16)).strip()
            lines = ["GET {} HTTP/1.1".format(path), "Host: {}:{}".format(host, port),
                     "Upgrade: websocket", "Connection: Upgrade",
                     "Sec-WebSocket-Key: " + key.decode(), "Sec-WebSocket-Version: 13"]
            for name in (headers or {}):
                lines.append("{}: {}".format(name, headers[name]))
            _write(sock, ("\r\n".join(lines) + "\r\n\r\n").encode())

            data = b""
            while b"\r\n\r\n" not in data:
                more = sock.read(1) if hasattr(sock, "read") else sock.recv(1)   # byte by byte: never read into the first frame
                if not more:
                    raise buddy_http.NetError("reset", "closed during the handshake")
                data += more
                if len(data) > 1024:
                    raise buddy_http.NetError("bad-reply", "handshake reply too long", False)
            lines = data.decode().split("\r\n")
            status = int(lines[0].split(" ")[1])
            if status in (401, 403):
                raise buddy_http.NetError("auth", "server refused the token", False)
            if status != 101:
                raise buddy_http.NetError("bad-reply", "upgrade refused: " + lines[0], False)
            accept = ""
            for line in lines[1:]:
                name, _, value = line.partition(":")
                if name.strip().lower() == "sec-websocket-accept":
                    accept = value.strip()
            expected = binascii.b2a_base64(hashlib.sha1(key + GUID).digest()).strip().decode()
            if accept != expected:
                raise buddy_http.NetError("bad-reply", "wrong Sec-WebSocket-Accept", False)
        except BaseException:
            sock.close()
            raise
        return cls(sock)

    def _send(self, opcode, payload):
        n = len(payload)
        key = os.urandom(4)
        if n < 126:
            head = bytes([0x80 | opcode, 0x80 | n])
        elif n < 65536:
            head = bytes([0x80 | opcode, 0x80 | 126, n >> 8, n & 255])
        else:
            raise ValueError("frame too big")
        _write(self.sock, head + key + _xor_mask(payload, key))

    def send_text(self, text):
        self._send(TEXT, text.encode())

    def send_binary(self, data):
        self._send(BINARY, data)

    def recv(self):
        """Wait for the next text or binary message. Pings are answered here."""
        while True:
            b0, b1 = _read_exact(self.sock, 2)
            opcode = b0 & 0x0F
            if not b0 & 0x80:
                raise ValueError("fragmented messages are not supported")
            n = b1 & 0x7F
            if n == 126:
                hi, lo = _read_exact(self.sock, 2)
                n = (hi << 8) | lo
            elif n == 127:
                raise ValueError("frame too big")
            if n > MAX_FRAME:
                raise ValueError("frame of {} bytes, limit {}".format(n, MAX_FRAME))
            payload = _read_exact(self.sock, n)          # server frames are not masked
            if opcode == PING:
                self._send(PONG, payload)
            elif opcode == CLOSE:
                self.open = False
                raise WsClosed("server closed the connection")
            elif opcode == TEXT:
                return "text", payload.decode()
            elif opcode == BINARY:
                return "binary", payload

    def close(self):
        if self.open:
            try:
                self._send(CLOSE, b"\x03\xe8")           # status 1000: normal closure
            except Exception:
                pass
        self.open = False
        self.sock.close()
