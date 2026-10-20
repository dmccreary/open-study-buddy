#!/usr/bin/env python3
"""Chapter 14: the WebSocket side of the buddy server.

    pip install websockets
    export BUDDY_TOKENS="pick-a-long-random-string"
    python3 ws_server.py                 # ws://0.0.0.0:8081/v1/stream
    python3 ws_server.py --tls server.pem server.key     # wss://

Why a WebSocket? One HTTP request carries one question and one answer, and each
needs its own connection and headers. A WebSocket is ONE connection that stays
open, and either side may send a small frame at any time. That lets the Pico
send audio while the student is still talking, and lets the Pico say "stop"
(barge-in) while the server is still sending speech.

The protocol (text frames are JSON, binary frames are raw 16-bit mono PCM at 12,800 Hz):

  Pico  -> server   {"event": "start", "rate": 12800, "volume": 40}   begin an utterance
  Pico  -> server   <binary frame>  ...                             audio chunks, any number
  Pico  -> server   {"event": "end"}                                done talking
  server -> Pico    {"type": "reply", "heard": ..., "speak": ..., "show": ..., "next_mode": ...}
  server -> Pico    <binary frame> ...                              the spoken answer, 1,024 bytes each
  server -> Pico    {"type": "audio_end"}
  Pico  -> server   {"event": "cancel"}                             barge-in: stop talking now
  server -> Pico    {"type": "cancelled"}

Authentication is the same X-Buddy-Token header as the HTTP server, checked in
the handshake, before any audio is accepted.
"""

import argparse
import asyncio
import json
import ssl
import sys
from http import HTTPStatus

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

import brain
import buddy_server as core
import tts

OUT_FRAME = 1024                    # bytes of speech per frame: one 40 ms audio frame


async def check_handshake(connection, request):
    """Runs before the connection is accepted."""
    if request.path != "/v1/stream":
        return connection.respond(HTTPStatus.NOT_FOUND, "no such endpoint\n")
    if core.TOKENS and not core.token_ok(request.headers.get("X-Buddy-Token", "")):
        print("REFUSED: missing or wrong token", file=sys.stderr)
        return connection.respond(HTTPStatus.UNAUTHORIZED, "missing or wrong X-Buddy-Token\n")
    return None


async def answer(ws, pcm, rate, volume):
    reply, speech = await asyncio.to_thread(core.answer_audio, pcm, rate)
    await ws.send(json.dumps({"type": "reply", **reply}))
    speech = tts.apply_volume(speech, volume)
    for start in range(0, len(speech), OUT_FRAME):
        await ws.send(speech[start:start + OUT_FRAME])      # waits if the Pico is slow to read
    await ws.send(json.dumps({"type": "audio_end"}))


async def handler(ws):
    audio = bytearray()
    rate, volume = core.DEVICE_RATE, 40
    speaking = None

    async def stop_speaking():
        nonlocal speaking
        if speaking and not speaking.done():
            speaking.cancel()
            try:
                await speaking
            except asyncio.CancelledError:
                pass
        speaking = None

    try:
        async for message in ws:
            if isinstance(message, bytes):
                if len(audio) + len(message) > core.MAX_AUDIO_BYTES:
                    await ws.close(1009, "too much audio")
                    return
                audio += message
                continue
            try:
                event = json.loads(message).get("event")
            except (ValueError, AttributeError):
                await ws.send(json.dumps({"type": "error", "error": "text frames must be JSON"}))
                continue
            if event == "start":
                await stop_speaking()
                audio.clear()
                body = json.loads(message)
                rate = int(body.get("rate", 0))
                volume = int(body.get("volume", 40))
                if rate != core.DEVICE_RATE:
                    await ws.close(1008, "rate must be {}".format(core.DEVICE_RATE))
                    return
            elif event == "end":
                if len(audio) % 2:
                    audio.pop()
                pcm = bytes(audio)
                audio.clear()
                speaking = asyncio.create_task(answer(ws, pcm, rate, volume))
            elif event == "cancel":
                await stop_speaking()
                audio.clear()
                await ws.send(json.dumps({"type": "cancelled"}))
            else:
                await ws.send(json.dumps({"type": "error", "error": "unknown event"}))
    except ConnectionClosed:
        pass
    finally:
        await stop_speaking()


async def main():
    parser = argparse.ArgumentParser(description="Open Study Buddy WebSocket server, chapter 14")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--no-auth", action="store_true")
    parser.add_argument("--tls", nargs=2, metavar=("CERT.pem", "KEY.pem"))
    parser.add_argument("--ping-interval", type=float, default=20,
                        help="seconds between pings (0 turns them off)")
    args = parser.parse_args()

    core.configure_tokens(args.no_auth)
    core.EVENTS = brain.load_events()
    context = None
    if args.tls:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(*args.tls)
    async with serve(handler, args.host, args.port, ssl=context,
                     process_request=check_handshake, max_size=64 * 1024,
                     ping_interval=args.ping_interval or None) as server:
        print("ws_server.py v1.0")
        print("{}://{}:{}/v1/stream  (auth {})".format(
            "wss" if context else "ws", args.host, args.port, "OFF" if not core.TOKENS else "on"))
        print("BUDDY_HOST = \"{}\"".format(core.lan_address()))
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nstopped")
