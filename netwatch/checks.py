import socket
import subprocess
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests

from .config import Target

@dataclass
class CheckResult:
    target: Target
    success: bool
    latency_ms: Optional[float]  
    message: str 

    def to_dict(self) -> dict:
        return {
            "target": self.target.model_dump(),
            "success": self.success,
            "latency_ms": self.latency_ms,
            "message": self.message,
        }

def ping_check(target: Target, timeout: float = 5.0) -> CheckResult:
    """
    Vérifie la connectivité IP avec ping.
    - Illustre la couche réseau (ICMP).
    - Utilise la commande 'ping' du système.
    """
    # '-c 1' = 1 paquet, '-W' timeout en secondes (linux)
    wait_s = max(1, int(timeout))
    cmd = ["ping", "-c", "1", "-W", str(wait_s), target.host]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout + 1,
        )
        success = proc.returncode == 0
        latency = None

        # Cherche 'time=X ms' dans la sortie
        for line in proc.stdout.splitlines():
            if "time=" in line:
                part = line.split("time=")[1]
                latency_str = part.split(" ")[0]  
                try:
                    latency = float(latency_str)
                except ValueError:
                    latency = None
                break

        message = "Ping OK" if success else (proc.stderr or "Ping failed")
        return CheckResult(
            target=target,
            success=success,
            latency_ms=latency,
            message=message,
        )
    except Exception as e:
        return CheckResult(
            target=target,
            success=False,
            latency_ms=None,
            message=f"Ping error: {e}",
        )

def tcp_check(target: Target, timeout: float = 5.0) -> CheckResult:
    """
    Vérifie si un port TCP est accessible.
    - Illustre la couche transport (TCP).
    """
    if target.port is None:
        return CheckResult(
            target=target,
            success=False,
            latency_ms=None,
            message="TCP check requires a port",
        )

    try:
        started = time.perf_counter()
        with socket.create_connection((target.host, target.port), timeout=timeout):
            pass
        latency_ms = (time.perf_counter() - started) * 1000.0
        return CheckResult(
            target=target,
            success=True,
            latency_ms=latency_ms,
            message="TCP connection successful",
        )
    except Exception as e:
        return CheckResult(
            target=target,
            success=False,
            latency_ms=None,
            message=f"TCP error: {e}",
        )


def http_check(target: Target, timeout: float = 5.0) -> CheckResult:
    """
    Vérifie un endpoint HTTP (ex: /health).
    - Illustre la couche application (HTTP).
    """
    path = target.path or "/"
    url = f"https://{target.host}{path}"
    try:
        resp = requests.get(url, timeout=timeout)
        success = resp.status_code == 200
        latency_ms = resp.elapsed.total_seconds() * 1000.0
        return CheckResult(
            target=target,
            success=success,
            latency_ms=latency_ms,
            message=f"HTTP {resp.status_code}",
        )
    except Exception as e:
        return CheckResult(
            target=target,
            success=False,
            latency_ms=None,
            message=f"HTTP error: {e}",
        )


def run_check(target: Target) -> CheckResult:
    """
    Route vers le bon type de check selon target.type.
    """
    if target.type == "ping":
        return ping_check(target)
    if target.type == "tcp":
        return tcp_check(target)
    if target.type == "http":
        return http_check(target)

    return CheckResult(
        target=target,
        success=False,
        latency_ms=None,
        message=f"Unknown check type: {target.type}",
    )


def check_ping(host: str, timeout: float = 5.0) -> CheckResult:
    target = Target(name=f"ping:{host}", host=host, type="ping")
    return ping_check(target, timeout=timeout)


def check_tcp(host: str, port: int, timeout: float = 5.0) -> CheckResult:
    target = Target(name=f"tcp:{host}:{port}", host=host, type="tcp", port=port)
    return tcp_check(target, timeout=timeout)


def check_http(url: str, timeout: float = 5.0) -> CheckResult:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid URL, expected absolute URL like https://example.com/path")
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL scheme must be http or https")

    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    target = Target(name=f"http:{url}", host=parsed.netloc, type="http", path=path)
    try:
        resp = requests.get(url, timeout=timeout)
        success = resp.status_code == 200
        latency_ms = resp.elapsed.total_seconds() * 1000.0
        return CheckResult(
            target=target,
            success=success,
            latency_ms=latency_ms,
            message=f"HTTP {resp.status_code}",
        )
    except Exception as e:
        return CheckResult(
            target=target,
            success=False,
            latency_ms=None,
            message=f"HTTP error: {e}",
        )
