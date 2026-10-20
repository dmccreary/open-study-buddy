# Chapter 13 code: Wi-Fi, HTTP, and Connecting to the Agent

Chapter: `docs/chapters/13-wifi-http-agent-link/index.md`

Two programs run in two places. The **buddy server** runs on your computer (or a
school Raspberry Pi) and needs only Python 3, nothing to install. Everything else
runs on the Pico.

```bash
# 1. On your computer: start the server and note the address it prints
cd src/chapters/13-wifi-http-agent-link/server
python3 buddy_server.py            # plain HTTP on port 8080, trusted classroom network only

# 2. Edit buddy_config.py: set BUDDY_HOST to that address (a line like
#    put this in buddy_config.py on the Pico:  BUDDY_HOST = "192.168.1.50")
#    Make sure the kit's secrets.py has wifi_ssid and wifi_pass.

# 3. Upload and run
cd src/chapters
./upload-chapter.sh 13 01-wifi-connect.py
```

The `server/` folder stays on your computer (`upload-chapter.sh` only uploads the
top-level `.py` files). Check the server with no Pico at all:
`python3 server/test_server.py`.

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-wifi-connect.py` | Pico + 2.4 GHz Wi-Fi + `secrets.py` | States print with times, an IP address appears, PASS |
| `02-ip-and-subnet.py` | none (also runs on a computer); on the Pico it checks `BUDDY_HOST` | Every table row says ok, PASS |
| `03-json-contract.py` | none (also runs on a computer) | Request is 73 bytes, reply 103 bytes, PASS |
| `04-raw-http-post.py` | none (also runs on a computer) | The request prints as plain text; Content-Length equals the body, PASS |
| `05-socket-post.py` | Wi-Fi + server running | Status 200, the contract reply, a round trip time, PASS |
| `06-requests-post.py` | Wi-Fi + server running (installs `requests` with `mip` if needed) | Status 200, response closed, PASS |
| `07-ask-buddy-display.py` | Display + MODE + Wi-Fi + server running | Status region: joining, online, asking, ok; the answer in the message region |
| `08-mdns-check.py` | Wi-Fi | A result line for every name; PASS (either answer is useful) |
| `buddy_config.py`, `wifi_link.py`, `rawhttp.py` | helper modules, imported by the tests | |
| `server/buddy_server.py`, `server/test_server.py`, `server/events.json` | your computer | `test_server.py` ends with PASS |

## The most important tests for the book

Please record these, so the chapter's estimates can become measurements:

- `05-socket-post.py`: the **connect time** and the **round trip time**, and the
  heap before and after.
- `06-requests-post.py`: the round trip time, the heap before and after, and the
  version of `requests` that `mip` installed.
- `01-wifi-connect.py`: how many milliseconds from "joining" to "connected" on
  your school network.
- `08-mdns-check.py`: does `<yourserver>.local` resolve? Write down
  `sys.version` too; this answers the chapter's open mDNS question.
- `07-ask-buddy-display.py`: with the server stopped, how long until "error"
  appears (it should match `REQUEST_TIMEOUT_S` or be much faster, for a refused
  connection).

## Wi-Fi, HTTP and credentials

- Wi-Fi name and password come from the kit's `secrets.py` (`wifi_ssid`,
  `wifi_pass`). It is git-ignored; never paste it into a chapter file.
- Chapter 13 sends no login. That is acceptable only on a trusted classroom
  network. Chapter 14's server asks for a token; if you upload Chapter 14's
  files afterwards, they replace `buddy_config.py` and `wifi_link.py` with
  versions that have more settings but the same names used here.

## What has been checked, and what has not

- The server was started and exercised with `test_server.py` (13 checks, all ok),
  and with the Pico scripts running on a computer.
- Every Pico script compiles, and `01` to `08` ran to completion on a computer
  against a fake `machine` / `network` / `time` layer, with real sockets talking
  to the real server. `01` was also run with a fake wrong password, a fake
  missing network, and a fake stuck connection. `05` and `07` were run with the
  server stopped (connection refused). This catches typos and logic errors.
- Nothing here has run on the Pico yet. Open questions: join times on a real
  network, round trip times, free heap after a request, which `requests` version
  `mip` installs, whether `str.format` `{:,}` and `str.partition` behave as on a
  computer in your firmware, and whether `.local` names resolve.
