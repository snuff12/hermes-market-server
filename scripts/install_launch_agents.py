"""Generate or install macOS supervisors without placing credentials in arguments."""

import argparse
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=["public", "local"], default="public")
    parser.add_argument("--install", action="store_true", help="Install and start the generated LaunchAgents")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("This helper supports macOS only. Use your operating system's service supervisor elsewhere.")
    python = str(ROOT / ".venv/bin/python")
    cli = [python, "-m", "hermes_market.cli"]
    if args.group == "public":
        cloudflared = shutil.which("cloudflared")
        if not cloudflared:
            parser.error("Install cloudflared before preparing public services.")
        services = {
            "public-directory": cli + ["--state", str(ROOT / ".state/public-directory"), "directory", "--port", "8995",
                "--public-origin", "https://market.0xeddie.kim", "--open-registration"],
            "public-seller": cli + ["testnet", "--config", str(ROOT / ".state/public/testnet/config.json")],
            "tunnel": [cloudflared, "tunnel", "--no-autoupdate", "--config", str(ROOT / ".state/cloudflare/config.json"),
                       "--metrics", "127.0.0.1:20246", "run", "hermes-market"],
        }
    else:
        services = {
            "simulation": cli + ["dev"],
            "local-seller": cli + ["testnet"],
            "buyer": cli + ["buyer-gateway", "--origin", "https://market-api.0xeddie.kim",
                           "--directory-origin", "https://market.0xeddie.kim"],
            "local-directory": cli + ["--state", str(ROOT / ".state/directory"), "directory",
                "--allow-seller", "http://127.0.0.1:8765", "--allow-seller", "http://127.0.0.1:8785"],
        }
    output = ROOT / ".state/launch-agents"
    output.mkdir(parents=True, mode=0o700, exist_ok=True)
    logs = ROOT / ".state/logs"
    logs.mkdir(parents=True, mode=0o700, exist_ok=True)
    for role, command in services.items():
        label = "kim.0xeddie.hermes-market." + role
        config = {"Label": label, "ProgramArguments": command, "WorkingDirectory": str(ROOT),
                  "RunAtLoad": True, "KeepAlive": True, "ThrottleInterval": 15,
                  "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
                  "StandardOutPath": str(logs / (role + ".log")), "StandardErrorPath": str(logs / (role + ".error.log"))}
        path = output / (label + ".plist")
        path.write_bytes(plistlib.dumps(config))
        path.chmod(0o600)
        if args.install:
            target = Path.home() / "Library/LaunchAgents" / path.name
            if target.exists():
                raise ValueError("This LaunchAgent already exists. Review it before replacing a running service.")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            target.chmod(0o600)
            subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(target)], check=True)
        print(("Installed " if args.install else "Prepared ") + label)


if __name__ == "__main__":
    main()
