# buddy_http.py -- a small HTTP/HTTPS client that is safe for a Pico
#
# What it adds to Chapter 13's raw sockets:
#   * a timeout on EVERY socket wait, plus a deadline for the whole request
#   * the request body is sent in chunks straight from a memoryview, so a
#     128,000-byte recording is never copied (head + body would need 128 KB more)
#   * the reply body can be handed to a function piece by piece (streaming), so
#     the speech audio never has to fit in memory
#   * every failure becomes a NetError with a kind and a "retryable" flag
#   * HTTPS with the certificate checked (cadata) or, for a lab demo only, not
#     checked
# It runs on the Pico and, unchanged, on a computer (that is how it was tested).

import errno
import json
import socket
import time

try:
    import ssl
except ImportError:
    ssl = None

MAX_HEAD = 2048


class NetError(Exception):
    """kind: timeout, refused, unreachable, reset, dns, auth, busy, bad-request,
    bad-reply, tls, other. retryable: would trying again later possibly help?"""

    def __init__(self, kind, detail="", retryable=True):
        Exception.__init__(self, "{}: {}".format(kind, detail) if detail else kind)
        self.kind = kind
        self.detail = detail
        self.retryable = retryable


def _codes(*names):
    return tuple(getattr(errno, n) for n in names if hasattr(errno, n))


_TIMEOUT = _codes("ETIMEDOUT")
_REFUSED = _codes("ECONNREFUSED")
_UNREACHABLE = _codes("EHOSTUNREACH", "ENETUNREACH", "ENETDOWN")
_RESET = _codes("ECONNRESET", "ECONNABORTED", "EPIPE", "ENOTCONN")


def classify(e):
    """Turn an OSError into a NetError (every network OSError is worth a retry)."""
    if isinstance(e, NetError):
        return e
    code = e.args[0] if e.args and isinstance(e.args[0], int) else None
    if code in _TIMEOUT or isinstance(e, getattr(socket, "timeout", ())):
        return NetError("timeout", "no answer in time")
    if code in _REFUSED:
        return NetError("refused", "nothing is listening at that address and port")
    if code in _UNREACHABLE:
        return NetError("unreachable", "no route to the server")
    if code in _RESET:
        return NetError("reset", "the connection was closed under us")
    if code == -2 or isinstance(e, getattr(socket, "gaierror", ())):
        return NetError("dns", "could not look up the server name")
    return NetError("other", repr(e))


def check_status(status, body=b""):
    """Raise NetError for a non-2xx status; say whether a retry could help."""
    if 200 <= status < 300:
        return
    text = ""
    try:
        text = json.loads(body).get("error", "")
    except Exception:
        pass
    if status in (401, 403):
        raise NetError("auth", "server refused the token ({})".format(text), False)
    if status in (408, 429) or status >= 500:
        raise NetError("busy", "server said {} {}".format(status, text), True)
    raise NetError("bad-request", "server said {} {}".format(status, text), False)


# ----------------------------------------------------------------------

def _deadline(total_s):
    return time.ticks_add(time.ticks_ms(), int(total_s * 1000))


def _check(deadline):
    if time.ticks_diff(time.ticks_ms(), deadline) > 0:
        raise NetError("timeout", "whole-request time limit reached")


def _send_all(sock, data, deadline):
    view = memoryview(data)
    while len(view):
        _check(deadline)
        n = sock.write(view) if hasattr(sock, "write") else sock.send(view)
        if not n:
            raise NetError("reset", "send made no progress")
        view = view[n:]


def _recv(sock, n):
    return sock.read(n) if hasattr(sock, "read") else sock.recv(n)


def _fill(sock, buf, deadline):
    """Read until buf is full or the server closes. Returns the byte count."""
    view = memoryview(buf)
    got = 0
    while got < len(buf):
        _check(deadline)
        if hasattr(sock, "readinto"):
            n = sock.readinto(view[got:])
        else:
            n = sock.recv_into(view[got:])
        if not n:
            break
        got += n
    return got


def open_socket(host, port, timeout_s, tls=False, cadata=None):
    """Connect; with tls=True also run the TLS handshake. cadata=None means the
    certificate is NOT checked (lab demos only); pass the certificate bytes to
    check it."""
    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
        sock = socket.socket()
        sock.settimeout(timeout_s)                # applies to connect, send, receive
        try:
            sock.connect(addr)
            if tls:
                sock = _wrap(sock, host, cadata)
        except BaseException:
            sock.close()
            raise
        return sock
    except OSError as e:
        raise classify(e)


def _wrap(sock, host, cadata):
    if ssl is None:
        raise NetError("tls", "this firmware has no ssl module", False)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if cadata:
        ctx.verify_mode = ssl.CERT_REQUIRED
        try:
            ctx.load_verify_locations(cadata=cadata)
        except (ValueError, OSError) as e:
            raise NetError("tls", "cannot use the certificate file: " + repr(e), False)
    else:
        try:
            ctx.check_hostname = False            # a computer needs this; MicroPython has no such attribute
        except AttributeError:
            pass
        ctx.verify_mode = ssl.CERT_NONE           # encrypted, but ANYONE can be the server
    try:
        return ctx.wrap_socket(sock, server_hostname=host)
    except OSError as e:
        raise NetError("tls", repr(e), False)


def _read_head(sock, deadline):
    data = b""
    while b"\r\n\r\n" not in data:
        _check(deadline)
        more = _recv(sock, 256)
        if not more:
            raise NetError("reset", "connection closed before the headers ended")
        data += more
        if len(data) > MAX_HEAD:
            raise NetError("bad-reply", "headers are too long", False)
    head, _, rest = data.partition(b"\r\n\r\n")
    lines = head.decode("utf-8").split("\r\n")
    parts = lines[0].split(" ", 2)
    if len(parts) < 2 or not parts[0].startswith("HTTP/"):
        raise NetError("bad-reply", "not an HTTP reply", False)
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    return int(parts[1]), headers, rest


def request(method, path, host, port, headers=None, body=None, chunk=2048,
            timeout_s=8, total_s=20, max_body=2048, tls=False, cadata=None,
            on_progress=None, sink=None, sink_buf=None):
    """One request. Returns (status, headers, body_bytes).

    body: bytes-like or None; sent in pieces of `chunk` bytes with a
          Content-Length header that is known up front.
    sink: if given, the reply body is NOT returned; it is passed to
          sink(memoryview) in pieces filled into sink_buf (one allocation).
    """
    deadline = _deadline(total_s)
    lines = ["{} {} HTTP/1.0".format(method, path),
             "Host: {}:{}".format(host, port), "Connection: close"]
    if body is not None:
        lines.append("Content-Length: {}".format(len(body)))
    for name in (headers or {}):
        lines.append("{}: {}".format(name, headers[name]))
    head = ("\r\n".join(lines) + "\r\n\r\n").encode("utf-8")

    sock = open_socket(host, port, timeout_s, tls, cadata)
    try:
        try:
            _send_all(sock, head, deadline)
            if body is not None:
                view = memoryview(body)
                sent = 0
                while sent < len(view):
                    piece = view[sent:sent + chunk]
                    _send_all(sock, piece, deadline)
                    sent += len(piece)
                    if on_progress:
                        on_progress(sent, len(view))
        except OSError as send_error:
            # A server that refuses an upload early (413 too big, 401 bad token)
            # may close while we are still sending. Its reason is waiting to be
            # read; if there is none, report the send error.
            try:
                status, rhead, rest = _read_head(sock, deadline)
            except (OSError, NetError):
                raise send_error
            return status, rhead, rest
        status, rhead, rest = _read_head(sock, deadline)
        length = rhead.get("content-length")
        length = int(length) if length is not None and length.isdigit() else None

        if sink is not None and 200 <= status < 300:
            if rest:
                sink(memoryview(rest))
            total = len(rest)
            while length is None or total < length:
                want = len(sink_buf) if length is None else min(len(sink_buf), length - total)
                n = _fill(sock, memoryview(sink_buf)[:want], deadline)
                if not n:
                    break
                sink(memoryview(sink_buf)[:n])
                total += n
            return status, rhead, b""

        if length is not None and length > max_body:
            raise NetError("bad-reply", "reply is {} bytes, limit {}".format(length, max_body), False)
        data = rest
        while length is None or len(data) < length:
            _check(deadline)
            more = _recv(sock, 256)
            if not more:
                break
            data += more
            if len(data) > max_body:
                raise NetError("bad-reply", "reply is longer than {} bytes".format(max_body), False)
        return status, rhead, data
    except OSError as e:
        raise classify(e)
    finally:
        sock.close()                              # always, even after an error
