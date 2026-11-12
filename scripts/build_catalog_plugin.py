"""Export reviewable plugin source without developer runtime or credential helpers.

The result is a candidate repository tree, not an uploaded or approved catalog
entry. No private state, server runner, model credentials or compiled UI is copied.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('__init__.py', 'plugin.py', 'authoring.py', 'contracts.py', 'drafts.py', 'buyer.py',
           'discovery.py', 'vault.py', 'wallet_auth.py', 'payment_signing.py', 'x402_adapter.py')


def build(destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError('Choose a new destination; existing exports are never overwritten.')
    destination.mkdir(parents=True)
    for name in ('__init__.py', 'plugin.yaml', 'desktop/plugin.js', 'skills/buy-service/SKILL.md', 'LICENSE'):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    for module in MODULES:
        target = destination / 'src/hermes_market' / module
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'src/hermes_market' / module, target)
    (destination / 'pyproject.toml').write_text('''[project]
name = "hermes-market-plugin"
version = "0.1.0"
requires-python = ">=3.11,<3.15"
dependencies = ["httpx==0.28.1", "jsonschema==4.26.0", "cryptography==50.0.2", "x402[evm,httpx,extensions]==2.27.0"]
''')
    (destination / 'README.md').write_text('''# Hermes Market

Discover owner-published APIs across sellers, create public service drafts from
selected skills, and buy results only after explicit human approval.

## Agent tools

- `service_search`: search the configured public service directory.
- `service_draft`: use the host `ctx.llm` interface to draft a public contract.
- `service_inspect` and `service_quote`: inspect a listing and request an exact quote.
- `service_purchase` and `service_status`: submit a stored approval and recover the original result.

## Install

Requires Hermes Agent 0.22.7 or newer. Tested with Hermes 0.23.0.

```sh
hermes plugins install snuff12/hermes-market
hermes plugins enable hermes-market
```

During catalog review, install from the repository above. Catalog installation
by the bare name becomes available only after a maintainer accepts the entry.
The catalog entry pins the exact reviewed source commit.

## Public marketplace and local workspaces

Fresh installations default to `buyer_mode: simulation`. Both `directory_origin`
and `buyer_origin` are empty. Search and listing tools return a setup error until
you set `directory_origin`; new slug-based requests require `buyer_origin`.
No buyer or discovery request is sent before the required origin is configured.
Saved purchases continue to use their original seller, even if these settings
are cleared. Testnet purchases still require an explicit `buyer_mode: testnet`.

The backend source and step-by-step setup are in
[hermes-market-server](https://github.com/snuff12/hermes-market-server/blob/main/docs/quickstart.md).
Start with its free simulation. Configure these settings in your active Hermes
profile, replacing the example state path with your actual private directory:

```yaml
plugins:
  enabled: [hermes-market]
  entries:
    hermes-market:
      settings:
        role: buyer
        directory_origin: http://127.0.0.1:8795
        buyer_mode: simulation
        buyer_origin: http://127.0.0.1:8765
        buyer_state_dir: /absolute/path/to/hermes-market-server/.state/buyer
```

Ask Hermes to find services with `service_search`, inspect one, and prepare a
quote. Payment approval is a separate human action. For owner drafting, use
`role: owner` or `both` and configure the private `draft_dir` shared with the
owner workspace. See the server guide for Base Sepolia setup and browser approval.

### Optional public demo

To opt in to the author-operated public demo, paste the following values into
the plugin's `settings` and replace both private paths with your actual gateway
paths:

```yaml
directory_origin: https://market.0xeddie.kim
buyer_origin: https://market-api.0xeddie.kim
buyer_mode: testnet
buyer_state_dir: /absolute/path/to/hermes-market-server/.state/buyer-testnet
buyer_vault_key_file: /absolute/path/to/hermes-market-server/.state/buyer-testnet/authorization.key
buyer_approval_origin: http://127.0.0.1:8767
```

From the server checkout, start the separate local approval gateway with matching
origins and paths. Replace the example paths consistently in both places:

```sh
.venv/bin/hermes-market buyer-gateway \\
  --origin https://market-api.0xeddie.kim \\
  --directory-origin https://market.0xeddie.kim \\
  --buyer-state /absolute/path/to/hermes-market-server/.state/buyer-testnet \\
  --vault-key-file /absolute/path/to/hermes-market-server/.state/buyer-testnet/authorization.key
```

This sends search queries to the demo directory. Inspecting or quoting a selected
listing contacts its seller; quote input and the seller-scoped wallet session go
to that seller. Review the seller origin before requesting a quote. These demo
hosts are optional and depend on the author's computer staying online. Mainnet
is disabled; this demo uses Base Sepolia test USDC.

Seller, directory and buyer gateway processes are separately operated services;
installing this plugin does not start them or expose your computer. The optional
Desktop page opens the optional public demo only after you click its labeled button,
and opens local My services and Purchases workspaces
in your browser. It is a launcher, not an embedded wallet.

## Disclosure

Network requests go to the explicitly configured directory and selected sellers.
Directory descriptions and results are untrusted data. The buyer keeps a local
SQLite ledger, encrypted seller sessions and signed payment authorizations in
its own configured state. A local browser gateway collects EOA wallet signatures;
the agent cannot approve or sign a payment. Shared budget reservations cover all
sellers. A purchase always recovers through its saved origin.

Owner mode reads explicitly selected SKILL.md files and static references, and
saves private draft bundles. The host LLM supplies inference; this package does
not read a provider credential store or include the developer token-copy helper.

The seller backend, its isolated model runtime, the service directory, the browser
wallet gateway, and public hosting are separate prerequisites. Current evidence
covers local simulation and Base Sepolia test USDC. Mainnet is unsupported.
There is no telemetry or self-updater. Source-only export; no compiled payloads.

## Catalog status

Catalog admission requires a maintainer-reviewed, SHA-pinned PR. Local validation
does not establish catalog acceptance. Validate this exact source tree with:

```sh
hermes plugins validate /path/to/hermes-market --install-deps
```

## License

MIT. See LICENSE.
''')
    files = {str(path.relative_to(destination)): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in destination.rglob('*') if path.is_file()}
    return {'directory': str(destination), 'files': files, 'developer_auth_helpers_included': False,
            'published': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.destination), indent=2))
