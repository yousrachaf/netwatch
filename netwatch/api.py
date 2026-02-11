from typing import Any, Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from netwatch.checks import check_http, check_ping, check_tcp

app = FastAPI(title="NetWatch", version="0.1.0")


class RunCheckRequest(BaseModel):
    type: Literal["ping", "http", "tcp"]
    host: Optional[str] = None
    url: Optional[str] = None
    port: Optional[int] = None
    timeout: float = Field(default=5.0, ge=0.1, le=60.0)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/check")
def run_check_api(payload: RunCheckRequest) -> Dict[str, Any]:
    try:
        if payload.type == "ping":
            if not payload.host:
                raise HTTPException(status_code=400, detail="host is required for ping")
            result = check_ping(payload.host, timeout=payload.timeout)

        elif payload.type == "http":
            if not payload.url:
                raise HTTPException(status_code=400, detail="url is required for http")
            result = check_http(payload.url, timeout=payload.timeout)

        elif payload.type == "tcp":
            if not payload.host or payload.port is None:
                raise HTTPException(status_code=400, detail="host and port are required for tcp")
            result = check_tcp(payload.host, payload.port, timeout=payload.timeout)

        else:
            raise HTTPException(status_code=400, detail="unknown check type")

        # Compatible dataclass / pydantic / dict
        if hasattr(result, "model_dump"):
            return result.model_dump()
        if hasattr(result, "__dict__"):
            return dict(result.__dict__)
        if isinstance(result, dict):
            return result
        return {"result": str(result)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
