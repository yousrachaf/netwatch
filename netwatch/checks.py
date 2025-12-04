from dataclasses import dataclass
from typing import Optional
from .config import Target

class CheckResult:
    target: Target
    success: bool
    latency_ms: Optional[float]
    message: str

def run_check(target: Target) -> CheckResult:
     return CheckResult(
        target=target,
        success=False,
        latency_ms=None,
        message="Check non implémenté",
    )