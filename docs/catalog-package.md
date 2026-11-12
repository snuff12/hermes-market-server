# Catalog submission package

The source checkout includes development, isolated runtime and verification
tools. The catalog candidate is a separate allowlisted source export:

```sh
.venv/bin/python scripts/build_catalog_plugin.py .state/catalog-plugin
```

Choose a new destination. Existing exports are never overwritten. The exporter
includes the Python plugin and its shared contract/buyer modules, `plugin.yaml`,
the buy-service skill, a minimal dependency declaration, a disclosure README,
and `desktop/plugin.js`. It excludes server runners, Docker tooling, developer
credential importers, personal state and compiled assets. The draft tool uses
the host `ctx.llm` interface. No provider credential store is read by the candidate.

## What installation provides

- Six tools: search, draft, inspect, quote, purchase and status.
- Listing-ID selection across seller origins, with exact live revision checks.
- Original-origin purchase recovery, signer-free approval and a shared budget.
- An optional Desktop SDK page and sidebar row with **Public demo**, **My services**,
  and **Purchases** launch buttons. The public demo opens only after an explicit
  click; owner and purchase workspaces use local addresses.

Fresh installations default to simulation with empty `directory_origin` and
`buyer_origin`. Unconfigured discovery and new seller requests fail before
network I/O. Demo addresses are documented as explicit opt-in settings in the
exported README. Original purchase recovery retains its saved seller origin;
testnet recovery requires the original buyer mode and private gateway state.

Seller APIs, the directory and the wallet gateway are separately operated
services. Installing the plugin does not start background servers, expose a
machine, approve transactions, or install the seller's skill. The existing
runtime credential-copy script remains a developer-only helper outside the
export, and is not a provider-auth route offered by this plugin.

## Verification and admission

Run the official check against the exact source tree that will be committed:

```sh
hermes plugins validate /absolute/path/to/catalog-plugin --install-deps
```

The candidate passed validation in a disposable pinned Hermes v0.23.0 container,
with no personal home or credential volumes. The official validator checks the
manifest, capability registration, dependencies, security scan, core override
and Desktop SDK surface. The dependency check also installs the four declared
requirements against the installed Hermes core constraints before importing the
payment/auth modules. See the [verification record](marketplace-verification-2026-11-07.json)
for the actual outcome. All 16 checks passed, the security scan was safe, and
there were zero warnings. This is not maintainer admission.

The source is now published at [snuff12/hermes-market](https://github.com/snuff12/hermes-market).
[Catalog PR #152641](https://github.com/NousResearch/hermes-agent/pull/152641)
requested changes to the `2a8588bba7df0b3482e52e17692be1a92a2abd0e` pin on
2026-11-12 KST: remove personal-host defaults and restore simulation as the
default mode. Payment and approval paths were reviewed positively. The revised
candidate uses the explicit configuration boundaries above. Maintainer acceptance
remains pending; the PR records the current source pin and validation result.

The [72.5-second English demo](https://github.com/snuff12/hermes-market/releases/tag/v0.1.0)
and its captions are public. This is a catalog application, not maintainer
approval or automatic inclusion. X posting and the hackathon form are tracked
separately in the [submission status](submission-2026-11-11.md). The public demo
uses a dedicated tunnel; plugin installation does not expose local services.

## References

- [Official catalog submission rules](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins/catalog-submission)
- [Desktop Plugin SDK](https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk)
