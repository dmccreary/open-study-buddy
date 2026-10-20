# rawhttp.py -- build an HTTP POST by hand, and read the reply by hand
#
# Chapter 13 shows the request as plain text before it uses the requests
# library. This module is that plain text. It runs on the Pico and, unchanged,
# on your computer (python3), which is how the chapter code was tested.

import json


def build_post(host, port, path, payload, extra_headers=None):
    """Return the full request as bytes: request line, headers, blank line, body.

    payload is a dict. Content-Length counts BYTES of the encoded body, not
    characters, so encode first and count after."""
    body = json.dumps(payload).encode("utf-8")
    lines = [
        "POST {} HTTP/1.0".format(path),
        "Host: {}:{}".format(host, port),
        "Content-Type: application/json",
        "Content-Length: {}".format(len(body)),
        "Connection: close",
    ]
    if extra_headers:
        for name in extra_headers:
            lines.append("{}: {}".format(name, extra_headers[name]))
    head = "\r\n".join(lines) + "\r\n\r\n"      # the blank line ends the headers
    return head.encode("utf-8") + body


def _recv(sock, n):
    if hasattr(sock, "read"):        # MicroPython sockets
        return sock.read(n)
    return sock.recv(n)              # CPython sockets


def read_response(sock, max_body=2048):
    """Read one HTTP reply from sock. Returns (status, headers, body).

    headers is a dict with lower-case names. Never reads more than max_body
    bytes of body, so a wrong or hostile server cannot fill the Pico's memory."""
    data = b""
    while b"\r\n\r\n" not in data:
        more = _recv(sock, 256)
        if not more:
            raise ValueError("connection closed before the headers ended")
        data += more
        if len(data) > 2048:
            raise ValueError("headers are too long")
    head, _, rest = data.partition(b"\r\n\r\n")
    lines = head.decode("utf-8").split("\r\n")
    parts = lines[0].split(" ", 2)              # "HTTP/1.0 200 OK"
    if len(parts) < 2 or not parts[0].startswith("HTTP/"):
        raise ValueError("not an HTTP reply: " + lines[0][:40])
    status = int(parts[1])
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()

    length = int(headers.get("content-length", "0"))
    if length > max_body:
        raise ValueError("reply body is {} bytes, limit {}".format(length, max_body))
    body = rest
    while len(body) < length:
        more = _recv(sock, min(256, length - len(body)))
        if not more:
            break
        body += more
    return status, headers, body[:length]
