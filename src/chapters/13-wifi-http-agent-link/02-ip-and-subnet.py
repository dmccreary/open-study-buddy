# Chapter 13, Test 02: IP addresses, netmasks, and "is it on my network?"
# Pure arithmetic on IPv4 addresses: turn an address into a number, apply a
# netmask, and decide whether two addresses are on the same local network and
# whether an address is in a private (RFC 1918) range. Runs on your COMPUTER
# (python3 02-ip-and-subnet.py) or on the Pico. On a Pico that has a
# secrets.py it also joins Wi-Fi and checks BUDDY_HOST against its own address.
#
# PASS: every table row says ok, and the last line says PASS.

NAME = "02-ip-and-subnet.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import sys


def to_int(address):
    a, b, c, d = [int(part) for part in address.split(".")]
    return (a << 24) | (b << 16) | (c << 8) | d


def to_text(number):
    return "{}.{}.{}.{}".format((number >> 24) & 255, (number >> 16) & 255,
                                (number >> 8) & 255, number & 255)


def network_of(address, netmask):
    """The network address: the part of the IP address the netmask keeps."""
    return to_int(address) & to_int(netmask)


def same_network(a, b, netmask):
    return network_of(a, netmask) == network_of(b, netmask)


def is_private(address):
    """RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16."""
    n = to_int(address)
    return (n >> 24 == 10
            or n >> 20 == (172 << 4) | 1          # 172.16.0.0 - 172.31.255.255
            or n >> 16 == (192 << 8) | 168)


def host_count(netmask):
    """Usable device addresses: all host bits except the all-0 and all-1 ones."""
    host_bits = 32 - bin(to_int(netmask)).count("1")
    return (1 << host_bits) - 2


# (Pico, netmask, server, expect same network, expect private)
CASES = (
    ("192.168.1.23", "255.255.255.0", "192.168.1.50", True, True),
    ("192.168.1.23", "255.255.255.0", "192.168.2.50", False, True),
    ("10.4.7.88", "255.255.0.0", "10.4.200.9", True, True),
    ("10.4.7.88", "255.255.255.0", "10.4.200.9", False, True),
    ("172.16.5.5", "255.255.240.0", "172.16.15.1", True, True),
    ("172.32.0.9", "255.255.255.0", "172.32.0.1", True, False),
    ("93.184.216.34", "255.255.255.0", "93.184.216.1", True, False),
)

ok = True
print()
print("{:<14} {:<15} {:<14} {:<12} {:>5} {:>5}  {}".format(
    "Pico", "netmask", "server", "network", "same", "priv", "check"))
for pico, mask, server, want_same, want_private in CASES:
    same = same_network(pico, server, mask)
    private = is_private(pico)
    good = same == want_same and private == want_private
    ok = ok and good
    print("{:<14} {:<15} {:<14} {:<12} {:>5} {:>5}  {}".format(
        pico, mask, server, to_text(network_of(pico, mask)),
        "yes" if same else "no", "yes" if private else "no", "ok" if good else "WRONG"))

print()
print("a /24 network (255.255.255.0) has {} usable addresses".format(host_count("255.255.255.0")))
print("a /16 network (255.255.0.0)   has {} usable addresses".format(host_count("255.255.0.0")))
ok = ok and host_count("255.255.255.0") == 254 and host_count("255.255.0.0") == 65534

if sys.implementation.name == "micropython":
    try:
        import buddy_config
        import wifi_link
        wlan = wifi_link.connect(timeout_ms=buddy_config.CONNECT_TIMEOUT_MS)
        ip, mask, gateway, dns = wlan.ifconfig()
        print()
        print("this Pico  : {} (netmask {})".format(ip, mask))
        print("private?   : {}".format("yes" if is_private(ip) else "NO -- this is not a classroom address"))
        print("server     : {}".format(buddy_config.BUDDY_HOST))
        print("same net?  : {}".format(
            "yes" if same_network(ip, buddy_config.BUDDY_HOST, mask)
            else "NO -- check BUDDY_HOST, or the server is on another network"))
        wifi_link.disconnect(wlan)
    except Exception as e:
        print()
        print("(skipped the live check: {})".format(e))

print()
print("PASS" if ok else "CHECK: a row is wrong")

# Try This
#   1. Add your own home or school address and netmask to CASES.
#   2. Why does 172.32.0.9 fail is_private() even though it starts with 172?
