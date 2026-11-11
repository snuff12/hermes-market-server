"""Prepare a fixed Cloudflare Tunnel route for public HTTP applications only."""

import json
from pathlib import Path
import uuid

from .public_http import public_origin


def write_config(path, tunnel_id, credentials_file, directory_origin, seller_origin, directory_port=8995, seller_port=8985):
    tunnel_id = str(uuid.UUID(tunnel_id))
    origins = [public_origin(directory_origin), public_origin(seller_origin)]
    if origins[0] == origins[1]:
        raise ValueError("Use separate directory and seller hostnames.")
    if (directory_port == seller_port or any(type(port) is not int or not 1024 <= port <= 65535
                                             for port in (directory_port, seller_port))):
        raise ValueError("Use separate public application listener ports between 1024 and 65535.")
    config = {"tunnel": tunnel_id, "credentials-file": str(Path(credentials_file).expanduser().resolve()),
              "ingress": [{"hostname": origin.removeprefix("https://"), "service": f"http://127.0.0.1:{port}",
                           "originRequest": {"httpHostHeader": origin.removeprefix("https://")}}
                          for origin, port in zip(origins, (directory_port, seller_port))]
                         + [{"service": "http_status:404"}]}
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # JSON is a YAML subset accepted by cloudflared. Never replace an existing route.
    with path.open("x") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")
    path.chmod(0o600)
    return {"config": str(path), "origins": origins,
            "next": "Validate the ingress, create the two exact DNS routes, then run cloudflared with this config."}
