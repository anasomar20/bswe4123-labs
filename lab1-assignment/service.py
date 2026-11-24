
import time
import socket
from datetime import datetime, timezone
import os

from fastapi import FastAPI

app = FastAPI(title="Service Health Monitor")

# Record when the service starts
start_time = time.time()
HEALTH_DELAY = float(os.getenv("HEALTH_DELAY", "0"))


@app.get("/info")
def info(delay: float = 0.0):
    if delay > 0:
        time.sleep(delay)

    return {
        "host": socket.gethostname(),
        "server_time": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
def health():
    if HEALTH_DELAY > 0:
        time.sleep(HEALTH_DELAY)

    uptime = time.time() - start_time

    return {
        "status": "ok",
        "uptime": round(uptime, 2)
    }
