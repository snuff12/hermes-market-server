# Catalog review follow-up · 2026-11-12

[Maintainer review](https://github.com/NousResearch/hermes-agent/pull/152641#pullrequestreview-5865515511)
requested changes to the `2a8588bba7df0b3482e52e17692be1a92a2abd0e` plugin pin.
Payment and approval paths received a positive review. The requested changes
concerned network destinations and buyer mode on a fresh installation.

## Changes

- Python and manifest defaults now leave `directory_origin` and `buyer_origin`
  empty and use `buyer_mode: simulation`.
- Unconfigured search, listing requests and new seller requests return a named
  setup error before HTTP requests or buyer-state creation. Invalid modes fail
  before a directory lookup.
- Existing status and purchase calls retain the seller origin in the original
  ledger. Removing the current origin settings does not reroute a paid purchase.
  The original mode, private state and testnet vault requirements still apply.
- The exported README and public-hosting guide document public demo addresses
  as explicit opt-in values, with matching gateway origins and private paths.
  They describe which directory and seller receive queries and quote input.
- The optional Desktop demo button is labeled explicitly and makes no request
  until the user selects it. The buyer skill does not choose public hosts or
  testnet mode on the user's behalf.

## Verification

- Full Python suite: **316 passed**. The unchanged web suite previously passed
  39 browser tests; this change modifies no web application components.
- Privacy/default regression cases against the prior source: **22 failed,
  1 passed**. All cases pass against the revised source.
- Missing, null and whitespace origins are covered across seven buyer/discovery
  calls, with HTTP blocked and no buyer database created.
- Recovery tests cover both status and purchase after seller changes or removal.
- Official `hermes plugins validate --install-deps --json`: **16 checks passed,
  zero warnings**, security scan safe. It ran against the standalone export in
  a disposable Hermes v0.23.0 container with no personal home or credentials.
- English content check: **127 text files and 135 filenames passed**.

Two independent read-only agents reviewed the final source and export. Both
passed the 37 targeted plugin, multiseller and export tests. One independently
loaded manifest defaults and confirmed zero HTTP requests for all seven
unconfigured calls; it also checked saved testnet routing and mode mismatch.
The other ran six additional blocked-HTTP probes and checked the final gateway
instructions. A missing public-directory flag in the demo gateway instructions
was found during review and corrected before release.

No live wallet approval, payment, service restart or tunnel change was needed.
These local checks and independent reviews do not establish maintainer approval;
catalog acceptance remains pending.
