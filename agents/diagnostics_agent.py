import platform
import socket
import subprocess
import time

# Keywords that make a ticket eligible for network diagnostics
NETWORK_KEYWORDS = [
    "vpn", "network", "internet", "wifi", "wi-fi", "connect", "connectivity",
    "dns", "unreachable", "timeout", "disconnect", "proxy", "remote access",
]

PING_TARGET = "8.8.8.8"
DNS_TARGET = "google.com"
REACH_TARGETS = [("google.com", 443), ("github.com", 443)]


def should_run(ticket_text: str) -> bool:
    text = ticket_text.lower()
    return any(k in text for k in NETWORK_KEYWORDS)


def _ping(host: str) -> str:
    flag = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        start = time.time()
        result = subprocess.run(
            ["ping", flag, "1", host],
            capture_output=True, text=True, timeout=8,
        )
        elapsed_ms = int((time.time() - start) * 1000)
        if result.returncode == 0:
            return f"Ping {host}: OK (~{elapsed_ms} ms)"
        return f"Ping {host}: FAILED (no reply)"
    except Exception as e:
        return f"Ping {host}: ERROR ({e})"


def _dns(host: str) -> str:
    try:
        start = time.time()
        ip = socket.gethostbyname(host)
        elapsed_ms = int((time.time() - start) * 1000)
        return f"DNS resolve {host}: OK -> {ip} ({elapsed_ms} ms)"
    except Exception as e:
        return f"DNS resolve {host}: FAILED ({e})"


def _reach(host: str, port: int) -> str:
    try:
        start = time.time()
        with socket.create_connection((host, port), timeout=5):
            pass
        elapsed_ms = int((time.time() - start) * 1000)
        return f"Reach {host}:{port}: OK ({elapsed_ms} ms)"
    except Exception as e:
        return f"Reach {host}:{port}: FAILED ({e})"


def run_diagnostics(ticket_text: str) -> list[str]:
    """Returns a list of real check results, or [] if the ticket isn't network-related."""
    if not should_run(ticket_text):
        return []
    results = [_ping(PING_TARGET), _dns(DNS_TARGET)]
    results += [_reach(h, p) for h, p in REACH_TARGETS]
    return results