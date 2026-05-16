Bridge between Odoo and Intuit QuickBooks Online — the only piece of the
farm pack that can't be composed from existing Odoo CE or OCA modules
because nothing equivalent exists.

**Import:** `farm.qbo.connection` holds Intuit OAuth tokens; the
`farm.qbo.import` model orchestrates a three-phase commit (pull → review →
commit) over the chart of accounts, vendors, customers, items, and
transactions. Every committed record carries a back-reference to its QBO
source so the import can be rolled back atomically. Mapping proposals come
from a deterministic rule layer (the `qbo_account_dictionary`) with a
confidence score; the AI layer (proprietary `ledoent_farm_ai` module) can
replace it via the `farm.ai.provider` interface for ambiguous items.

**Export (v1):** Generate Intuit IIF / QBO Online CSV from Odoo journals so
the farmer's CPA can round-trip year-end into QBO Desktop.

**MVP scope:** Stub mode when `intuit-oauth` / `python-quickbooks` libs are
not installed (CI base image, design-partner sandboxes without Intuit
credentials) — the puller returns a small fixture so the full UI is
testable. Real OAuth flow ships in v1.
