from dataclasses import dataclass
from typing import Optional
from .config import Target

@dataclass
class CheckResult:
    target: Target
    success: bool
    latency_ms: Optional[float]  
    message: str 

def ping_check(target: Target) -> CheckResult:
    """
    Vérifie la connectivité IP avec ping.
    - Illustre la couche réseau (ICMP).
    - Utilise la commande 'ping' du système.
    """
    # '-c 1' = 1 paquet, '-W 1' = timeout 1 seconde linux
    cmd = ["ping", "-c", "1", "-W", "1", target.host]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        success = proc.returncode == 0
        latency = None

        # Cherche 'time=X ms' dans la sortie
        for line in proc.stdout.splitlines():
            if "time=" in line:
                part = line.split("time=")[1]
                latency_str = part.split(" ")[0]  
                latency = float(latency_str)
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

def tcp_check(target: Target) -> CheckResult:
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

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)

    try:
        s.connect((target.host, target.port))
        s.close()
        return CheckResult(
            target=target,
            success=True,
            latency_ms=None,
            message="TCP connection successful",
        )
    except Exception as e:
        return CheckResult(
            target=target,
            success=False,
            latency_ms=None,
            message=f"TCP error: {e}",
        )


def http_check(target: Target) -> CheckResult:
    """
    Vérifie un endpoint HTTP (ex: /health).
    - Illustre la couche application (HTTP).
    """
    path = target.path or "/"
    url = f"https://{target.host}{path}"
    try:
        resp = requests.get(url, timeout=2.0)
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