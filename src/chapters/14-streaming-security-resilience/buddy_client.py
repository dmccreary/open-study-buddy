# buddy_client.py -- everything the device says to the buddy server, in one place
#
# ask(text)                 POST /v1/ask      the Chapter 13 contract
# voice(pcm, nbytes)        POST /v1/voice    a recording, uploaded in chunks
# speech(path, sink, buf)   GET  /v1/speech/..  the spoken answer, streamed
# events()                  GET  /v1/events   the school events, for the offline cache
#
# Every call carries the token in an X-Buddy-Token header. The token lives in
# secrets.py (buddy_token = "..."), never in this file. With retries=True a call
# retries the failures that are worth retrying, waiting longer each time.

import json

import backoff
import buddy_config as cfg
import buddy_http

try:
    import secrets
    TOKEN = getattr(secrets, "buddy_token", "")
except ImportError:
    TOKEN = ""

_cadata = None


def _ca():
    """The certificate to trust, read once. None when HTTPS is off."""
    global _cadata
    if cfg.USE_TLS and _cadata is None:
        with open(cfg.CA_FILE, "rb") as f:
            _cadata = f.read()
    return _cadata


def _call(method, path, extra=None, body=None, **kw):
    headers = {"X-Buddy-Token": TOKEN, "X-Buddy-Device": cfg.DEVICE_ID}
    if extra:
        headers.update(extra)
    tls = cfg.USE_TLS
    port = cfg.BUDDY_TLS_PORT if tls else cfg.BUDDY_PORT
    return buddy_http.request(
        method, path, cfg.BUDDY_HOST, port, headers, body,
        chunk=cfg.UPLOAD_CHUNK_BYTES, timeout_s=cfg.REQUEST_TIMEOUT_S,
        total_s=cfg.TOTAL_TIMEOUT_S, max_body=cfg.MAX_REPLY_BYTES,
        tls=tls, cadata=_ca() if tls else None, **kw)


def _json_call(method, path, extra=None, body=None, **kw):
    status, headers, data = _call(method, path, extra, body, **kw)
    buddy_http.check_status(status, data)
    try:
        return json.loads(data)
    except ValueError:
        raise buddy_http.NetError("bad-reply", "reply is not JSON", False)


def ask(text, on_wait=None, retries=True):
    request = json.dumps({"device": cfg.DEVICE_ID, "kind": "question", "text": text})
    call = lambda: _json_call("POST", "/v1/ask",
                              {"Content-Type": "application/json"}, request.encode())
    return _with_retry(call, on_wait, retries)


def voice(pcm, nbytes, rate, on_progress=None, on_wait=None, retries=True):
    """Upload nbytes of 16-bit mono audio. Returns the reply dict (with 'heard'
    and, when the server made speech, 'audio': the path to fetch it from)."""
    body = memoryview(pcm)[:nbytes]
    extra = {"Content-Type": "application/octet-stream", "X-Audio-Rate": str(rate)}
    call = lambda: _json_call("POST", "/v1/voice", extra, body, on_progress=on_progress)
    return _with_retry(call, on_wait, retries)


def speech(path, volume, sink, buf, on_wait=None):
    """Stream the spoken answer into sink(memoryview). Not retried: a retry would
    start the sentence again after part of it was already played."""
    status, headers, _ = _call("GET", "{}?volume={}".format(path, volume), sink=sink, sink_buf=buf)
    buddy_http.check_status(status)
    return int(headers.get("x-audio-rate", "0"))


def events(on_wait=None):
    return _json_call("GET", "/v1/events")


def _with_retry(call, on_wait, retries):
    if not retries:
        return call()
    return backoff.retry(call, cfg.RETRY_ATTEMPTS, cfg.BACKOFF_BASE_MS,
                         cfg.BACKOFF_CAP_MS, on_wait)
