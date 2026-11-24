"""Open a private tunnel from this PC to the VPS Qwen API; leave the terminal open.
SSH asks for authentication itself. This script never reads or saves the password.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import argparse
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", required=True, help="Your SSH login name, not the password.")
    parser.add_argument("--host", default="173.208.151.137")
    parser.add_argument("--local-port", type=int, default=18084)
    args = parser.parse_args()
    if not 1024 <= args.local_port <= 65535:
        parser.error("Choose a local port between 1024 and 65535.")
    if not shutil.which("ssh"):
        parser.error("Install the OpenSSH client first.")
    if args.user.startswith("-") or args.host.startswith("-"):
        parser.error("Invalid SSH destination.")
    print(f"Qwen API will be available at http://127.0.0.1:{args.local_port}", flush=True)
    command = [
        "ssh",
        "-N",
        "-T",
        "-o",
        "ExitOnForwardFailure=yes",
        "-o",
        "ServerAliveInterval=30",
        "-o",
        "ServerAliveCountMax=3",
        "-L",
        f"127.0.0.1:{args.local_port}:127.0.0.1:18084",
        f"{args.user}@{args.host}",
    ]
    try:
        raise SystemExit(subprocess.call(command))
    except KeyboardInterrupt:
        print("Tunnel closed.")


if __name__ == "__main__":
    main()
