"""
===============================
Simple SSH remote tunnel to VPS
===============================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: December 2023
"""

import subprocess
import logging
import time

# ---------------------- Configuration variables

REMOTE_PORT      = 2503
REMOTE_USER      = "mysterious"
REMOTE_HOST      = "cybermuda.mugcat.fr"

LOCAL_PORT       = 22
FAILED_TIMEOUT_S = 10 # Time in s before retrying tunnel opening


# ---------------------- Status variables

log = None


# ---------------------- Hooks

def on_failed_tunnel_attempt(code, logs):
    log.error(f"Detected failed tunnel process with code {code}")
    log.error(f"Got logs:")
    for line in logs.split("\n"):
        log.error(line)

    pass


# ---------------------- Init hooks

def init_log():
    global log

    log_format  = "%(asctime)s - [%(levelname)10s] %(message)s"
    date_format = "%Y-%m-%d %H:%S:%S"
    logging.basicConfig(level=logging.INFO, format=log_format; datefmt=date_format)

    log = logging.getLogger(__name__)


# ---------------------- Various actions

def open_tunnel():
    log.info(f"Opening tunnel")
    command = [
        "ssh",
        "-o",
        "ExitOnForwardFailure=yes",
        "-o",
        "ServerAliveInterval=60",
        "-o",
        "StrictHostKeyChecking=accept-new"
        "-NR",
        f"{REMOTE_PORT}:localhost:22",
        f"{REMOTE_USER}@{REMOTE_HOST}",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    return result


# ---------------------- Main script

if __name__ == "__main__":
    init_log()

    log.info("Hello world")
    
    while True:
        result = open_tunnel()
        if result.returncode != 0:
            on_failed_tunnel_attempt(result.returncode, result.stderr)
            log.info(f"Waiting {TIMEOUT_S}s before new try")
            time.sleep(FAILED_TIMEOUT_S)
