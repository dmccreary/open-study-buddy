#!/usr/bin/env python3
"""Chapter 14: test the buddy server (HTTP and WebSocket) without a Pico.

    pip install websockets
    python3 test_client.py

It starts buddy_server.py and ws_server.py itself on spare ports with a random
token, sends them what the Pico would send (and a lot of things the Pico should
never send), checks the answers, and shuts both down. It also tries HTTPS and
WSS with a throw-away certificate if `openssl` is installed.

PASS: every line says ok, and the last line says PASS.
"""

import asyncio
import http.client
import json
import os
import secrets
import socket
import ssl
import subprocess
import sys
import tempfile
import time

import websockets

HERE = os.path.dirname(os.path.abspath(__file__))
HTTP_PORT, WS_PORT, TLS_PORT, WSS_PORT = 18180, 18181, 18182, 18183
RATE = 12800
problems = []


def check(label, condition, detail=""):
    print("{:<5}{}{}".format("ok" if condition else "FAIL", label, "  " + str(detail) if detail else ""))
    if not condition:
        problems.append(label)


def spawn(script, env, *args):
    process = subprocess.Popen([sys.executable, os.path.join(HERE, script), *args],
                               env={**os.environ, **env}, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
    return process


def wait_for(port, seconds=5):
    end = time.time() + seconds
    while time.time() < end:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            return True
        except OSError:
            time.sleep(0.1)
    return False


def tone(seconds, amplitude=8000, freq=300):
    import array, math
    n = int(seconds * RATE)
    return array.array("h", [int(amplitude * math.sin(2 * math.pi * freq * i / RATE))
                             for i in range(n)]).tobytes()


def call(method, path, body=None, headers=None, port=HTTP_PORT, tls_context=None, **kw):
    if tls_context:
        conn = http.client.HTTPSConnection("127.0.0.1", port, timeout=10, context=tls_context)
    else:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        conn.request(method, path, body=body, headers=headers or {}, **kw)
        r = conn.getresponse()
        return r.status, dict((k.lower(), v) for k, v in r.getheaders()), r.read()
    finally:
        conn.close()


def http_tests(old, new):
    good = {"X-Buddy-Token": new}
    print("-- HTTP, login")
    s, h, b = call("GET", "/v1/health")
    check("health needs no token", s == 200, b.decode())
    s, h, b = call("POST", "/v1/ask", "{}")
    check("no token: 401", s == 401, b.decode())
    s, h, b = call("POST", "/v1/ask", "{}", {"X-Buddy-Token": "wrong-wrong-wrong-wrong"})
    check("wrong token: 401", s == 401)
    ask = json.dumps({"device": "desk-07", "kind": "question", "text": "when is my next test"})
    s, h, b = call("POST", "/v1/ask", ask, good)
    reply = json.loads(b)
    check("right token: 200 and the Chapter 1 answer", s == 200 and reply["speak"] == "Your next test is Biology on Friday.")
    s, h, b = call("POST", "/v1/ask", ask, {"X-Buddy-Token": old})
    check("old token still works during rotation", s == 200)
    s, h, b = call("GET", "/v1/events", None, good)
    check("events list for the offline cache", s == 200 and len(json.loads(b)) == 3)

    print("-- HTTP, voice")
    pcm = tone(3.0)
    s, h, b = call("POST", "/v1/voice", pcm, {**good, "X-Audio-Rate": str(RATE)})
    voice = json.loads(b)
    check("3 s upload ({:,} bytes): 200".format(len(pcm)), s == 200, b.decode()[:100])
    check("transcript and contract fields", {"heard", "speak", "show", "next_mode", "audio"} <= set(voice))
    s, h, speech = call("GET", voice["audio"] + "?volume=40", None, good)
    import array
    samples = array.array("h"); samples.frombytes(speech)
    peak = max(abs(x) for x in samples)
    check("speech is 16-bit mono at 12,800 Hz", s == 200 and h["x-audio-rate"] == "12800" and len(speech) % 2 == 0,
          "{:,} bytes = {:.2f} s".format(len(speech), len(speech) / 2 / RATE))
    check("volume 40 puts the peak near 40% of full scale", 9000 < peak < 13500, peak)
    check("Content-Length matches the body", int(h["content-length"]) == len(speech))
    s, h, b = call("GET", voice["audio"], None)
    check("speech needs the token too", s == 401)
    s, h, b = call("POST", "/v1/voice", bytes(RATE * 2), {**good, "X-Audio-Rate": str(RATE)})
    check("silence is heard as nothing", json.loads(b)["heard"] == "" and "catch" in json.loads(b)["speak"])
    s, h, b = call("POST", "/v1/voice", pcm, {**good, "X-Audio-Rate": "16000"})
    check("wrong rate: 400", s == 400)
    s, h, b = call("POST", "/v1/voice", pcm[:-1], {**good, "X-Audio-Rate": str(RATE)})
    check("odd byte count: 400", s == 400)
    raw = socket.create_connection(("127.0.0.1", HTTP_PORT), timeout=5)
    raw.sendall("POST /v1/voice HTTP/1.1\r\nX-Buddy-Token: {}\r\nX-Audio-Rate: {}\r\nTransfer-Encoding: chunked\r\n\r\n"
                "800\r\n".format(new, RATE).encode() + pcm[:2048] + b"\r\n0\r\n\r\n")
    answer = raw.recv(200).decode(errors="replace"); raw.close()
    check("Transfer-Encoding: chunked is refused with 411", " 411 " in answer.split("\r\n")[0])
    raw = socket.create_connection(("127.0.0.1", HTTP_PORT), timeout=5)
    raw.sendall("POST /v1/voice HTTP/1.0\r\nX-Buddy-Token: {}\r\nX-Audio-Rate: {}\r\nContent-Length: 300000\r\n\r\n"
                .format(new, RATE).encode())
    answer = raw.recv(200).decode(errors="replace"); raw.close()
    check("300,000-byte upload is refused with 413 before it is read", " 413 " in answer.split("\r\n")[0])

    print("-- HTTP, practice endpoints")
    t = time.time()
    s, h, b = call("GET", "/v1/slow?ms=700", None, good)
    check("slow endpoint waits", s == 200 and time.time() - t >= 0.65, "{:.2f} s".format(time.time() - t))
    codes = [call("GET", "/v1/flaky?fail=2", None, good)[0] for _ in range(4)]
    check("flaky endpoint: 503, 503, 200, 503", codes == [503, 503, 200, 503], codes)


async def ws_tests(old, new, port=WS_PORT, scheme="ws", context=None):
    print("-- {}".format(scheme.upper()))
    url = "{}://127.0.0.1:{}/v1/stream".format(scheme, port)
    try:
        async with websockets.connect(url, ssl=context):
            check("no token is refused", False)
    except websockets.exceptions.InvalidStatus as e:
        check("no token is refused at the handshake", e.response.status_code == 401)
    async with websockets.connect(url, additional_headers={"X-Buddy-Token": new}, ssl=context) as ws:
        pcm = tone(2.0)
        await ws.send(json.dumps({"event": "start", "rate": RATE, "volume": 40}))
        frames = 0
        for i in range(0, len(pcm), 1024):
            await ws.send(pcm[i:i + 1024])
            frames += 1
        await ws.send(json.dumps({"event": "end"}))
        reply = json.loads(await ws.recv())
        check("reply arrives as text, {:,} frames sent".format(frames), reply["type"] == "reply" and reply["next_mode"] == "clock")
        got = 0
        while True:
            m = await ws.recv()
            if isinstance(m, bytes):
                got += len(m)
                assert len(m) <= 1024
            else:
                check("audio_end follows the audio", json.loads(m)["type"] == "audio_end")
                break
        check("speech arrives in frames of at most 1,024 bytes", got > 0 and got % 2 == 0, "{:,} bytes".format(got))

        await ws.send(json.dumps({"event": "start", "rate": RATE, "volume": 40}))
        await ws.send(pcm[:4096])
        await ws.send(json.dumps({"event": "end"}))
        await ws.recv()                                  # the reply text
        await ws.send(json.dumps({"event": "cancel"}))   # barge-in
        while True:
            m = await ws.recv()
            if not isinstance(m, bytes) and json.loads(m)["type"] == "cancelled":
                break
        check("cancel (barge-in) is acknowledged", True)
        await ws.send(json.dumps({"event": "start", "rate": RATE, "volume": 40}))
        await ws.send(pcm[:4096])
        await ws.send(json.dumps({"event": "end"}))
        again = json.loads(await ws.recv())
        check("the connection still works after a cancel", again["type"] == "reply")
    async with websockets.connect(url, additional_headers={"X-Buddy-Token": new}, ssl=context) as ws:
        await ws.send(json.dumps({"event": "start", "rate": RATE, "volume": 40}))
        try:
            for _ in range(300):
                await ws.send(bytes(1024))               # 307,200 bytes > the 256,000 limit
            await ws.recv()
            check("too much audio closes the connection", False)
        except websockets.exceptions.ConnectionClosed as e:
            check("too much audio closes the connection (1009)", e.rcvd is not None and e.rcvd.code == 1009)


def main():
    old = secrets.token_urlsafe(18)
    new = secrets.token_urlsafe(18)
    env = {"BUDDY_TOKENS": new + "," + old}
    procs = [spawn("buddy_server.py", env, "--port", str(HTTP_PORT), "--debug"),
             spawn("ws_server.py", env, "--port", str(WS_PORT))]
    tmp = None
    try:
        check("servers started", wait_for(HTTP_PORT) and wait_for(WS_PORT))
        http_tests(old, new)
        asyncio.run(ws_tests(old, new))

        if subprocess.run(["which", "openssl"], capture_output=True).returncode == 0:
            tmp = tempfile.mkdtemp()
            subprocess.run([os.path.join(HERE, "make-cert.sh"), "127.0.0.1", tmp], check=True,
                           capture_output=True)
            cert, key = os.path.join(tmp, "server.pem"), os.path.join(tmp, "server.key")
            procs.append(spawn("buddy_server.py", env, "--port", str(TLS_PORT), "--tls", cert, key))
            procs.append(spawn("ws_server.py", env, "--port", str(WSS_PORT), "--tls", cert, key))
            check("TLS servers started", wait_for(TLS_PORT) and wait_for(WSS_PORT))
            print("-- HTTPS")
            good = ssl.create_default_context(cafile=cert)
            s, h, b = call("GET", "/v1/health", port=TLS_PORT, tls_context=good)
            check("HTTPS works when the client trusts the certificate", s == 200)
            try:
                call("GET", "/v1/health", port=TLS_PORT, tls_context=ssl.create_default_context())
                check("an untrusting client refuses the self-signed certificate", False)
            except ssl.SSLError:
                check("a client that does not trust the certificate refuses it", True)
            with open(os.path.join(tmp, "ca.der"), "rb") as f:
                der = f.read()
            der_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            der_ctx.load_verify_locations(cadata=der)       # exactly what the Pico does with ca.der
            s, h, b = call("GET", "/v1/health", port=TLS_PORT, tls_context=der_ctx)
            check("trusting the DER file (as the Pico does) works", s == 200, "ca.der is {} bytes".format(len(der)))
            asyncio.run(ws_tests(old, new, WSS_PORT, "wss", good))
    finally:
        for p in procs:
            p.terminate()
        for p in procs:
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
    print()
    print("PASS: the server does what the chapter says." if not problems
          else "CHECK: {} problem(s): {}".format(len(problems), "; ".join(problems)))


if __name__ == "__main__":
    main()
