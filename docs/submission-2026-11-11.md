# Submission status · 2026-11-11

| Artifact | Location |
| --- | --- |
| Public marketplace | https://market.0xeddie.kim |
| Demo seller | https://market-api.0xeddie.kim |
| Plugin | https://github.com/snuff12/hermes-market |
| Server and setup | https://github.com/snuff12/hermes-market-server |
| Plugin source pin | `2a8588bba7df0b3482e52e17692be1a92a2abd0e` |
| Catalog PR | https://github.com/NousResearch/hermes-agent/pull/152641 |
| English narrated video | https://github.com/snuff12/hermes-market/releases/download/v0.1.0/hermes-market-demo.mp4 |
| Captions and sanitized verification | https://github.com/snuff12/hermes-market/releases/tag/v0.1.0 |

The catalog PR now contains only `plugin-catalog/hermes-market.yaml`. It matches
the full source pin, six declared tools, current screenshots and public hosting
instructions. Official structural validation passed with no warnings. Maintainer
review and catalog acceptance remain pending.

The exact plugin pin passed official validation in GitHub CI: 16 checks and zero
warnings. A fresh disposable Hermes v0.23 host loaded all six tools and found both
public HTTPS testnet services using the defaults. Server CI passed the production
build, English check, 290 Python tests and 39 browser tests. Public commits are
SSH-signed; GitHub reported verified signatures with reason `valid`.

The video is 72.5 seconds, H.264/AAC, with English narration and burned-in captions.
It shows the public market, HTTPS registration, storefront, actual captured native
tool output, private owner workflows and previous local testnet purchase evidence.
It creates no wallet signature or new payment. The release download was compared
to the local verified artifact by SHA256.

## Hosting and purchase limits

The named Cloudflare Tunnel exposes only the directory and public testnet seller.
Both run on the host computer and stop when it is off or disconnected. Owner
management, buyer signing and the isolated Hermes Runs endpoint remain private.
Mainnet is disabled. Public prices and payments use Base Sepolia test USDC.

Original local paid results, encrypted authorizations and runtime results remain
readable. Existing purchases retain their original origin. A restored backup
missing a run ID can remain unknown after its remote admission reservation expires;
this never authorizes another run or payment.

## Entrant handoff

The entrant will publish the X post and submit the final hackathon form separately.
Neither action has been performed. Catalog acceptance is also a separate state.
No additional account details are required for the completed source preparation.
