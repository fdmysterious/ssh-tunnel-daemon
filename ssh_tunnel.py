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

from   argparse import ArgumentParser


# ---------------------- Status variables

log = None


# ---------------------- Hooks

def on_failed_tunnel_attempt(code, logs):
    log.error(f"Detected failed tunnel process with code {code}")
    log.error(f"Got logs:")
    for line in logs.split("\n"):
        log.error(line)

    # TODO # add misc log features here


# ---------------------- Init hooks

def init_log():
    global log

    log_format  = "%(asctime)s - [%(levelname)10s] %(message)s"
    date_format = "%Y-%m-%d %H:%S:%S"
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)

    log = logging.getLogger(__name__)


def parse_arguments():
    parser = ArgumentParser(description="Start and monitor remote SSH tunnel")
    parser.add_argument("--remote_port"     , help="Remote access port"               , type=int,   required= True)
    parser.add_argument("--remote_user"     , help="Remote user"                      , type=str,   required= True)
    parser.add_argument("--remote_host"     , help="Remote host"                      , type=str,   required= True)
    parser.add_argument("--local_port"      , help="Local port"                       , type=int,   default = 22  )
    parser.add_argument("--failed_timeout_s", help="Time between each tunnel try in s", type=float, default = 10.0)

    args = parser.parse_args()

    return args


# ---------------------- Various actions

def open_tunnel(
    local_port,
    remote_port,
    remote_user,
    remote_host
):
    log.info(f"Opening tunnel")
    command = [
        "ssh",
        "-o",
        "ExitOnForwardFailure=yes",
        "-o",
        "ServerAliveInterval=60",
        "-o",
        "StrictHostKeyChecking=yes", # User must connect one time using user before launching this script to create the correct known_hosts entry
        "-NR",
        f"{remote_port}:localhost:{local_port}",
        f"{remote_user}@{remote_host}",
    ]
    log.debug(command)

    result = subprocess.run(command, capture_output=True, text=True)
    return result


# ---------------------- Main script

if __name__ == "__main__":
    init_log()
    args = parse_arguments()

    log.info("Hello world")
    
    while True:
        result = open_tunnel(
            local_port  = args.local_port,
            remote_port = args.remote_port,
            remote_user = args.remote_user,
            remote_host = args.remote_host,
        )

        if result.returncode != 0:
            on_failed_tunnel_attempt(result.returncode, result.stderr)
            log.info(f"Waiting {args.failed_timeout_s}s before new try")
            time.sleep(float(args.failed_timeout_s))
