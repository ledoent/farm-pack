# Competitive landscape — US farm software (2026-05)

Snapshot of where ledoent/farm-pack sits relative to the ag-software products a US SMB
farmer is likely to evaluate. Use this to inform positioning, feature prioritization,
and the eventual marketing page.

**Status:** first version. No prior competitive analysis was merged to the repo before
this file.

## What we've built (farm-pack today)

- **Distribution shape**: Odoo 19 industry pack (`farm_pack` umbrella + ~13 leaf
  modules). Composition over invention — leans on Odoo CE sale/stock/account/website +
  selected OCA repos; thin glue for the farm-specific bits.
- **Four core jobs** (per the composition plan):
  1. QuickBooks compatibility (`farm_quickbooks_io`)
  2. Website (storefront + market-event preorder UI)
  3. Online ordering (sale.order + portal)
  4. Weekly delivery routes (`farm_delivery_route_orders` — stock.picking.batch glue)
- **Geo slice (v1, just shipped)**: `farm_field_geo` (PostGIS polygon + acreage
  compute), `farm_field_overlays` (USDA CDL + NRCS Soil), `farm_observation` (geotagged
  photos + urgency), `farm_water_source`, `farm_fence`.
- **Cross-cutting glue**: `farm_base` (mixins, including the new `farm.rank.mixin` for
  selection→priority sort), `farm_csa_contract_glue`, `farm_onboarding` (4-screen
  wizard), `farm_market_event` + `farm_market_event_website`, `farm_egg_production`.
- **No custom design system applied yet** — frontend surfaces are stock Odoo backend
  chrome + Odoo's storefront templates. `oca-design-system` exists
  (`OdsCardTile`/`Chip`/`Avatar`/`Icon`) but isn't wired into farm-pack views yet.
- **No marketing site yet.**

## Competitors

### Ambrook — `ambrook.com`

- **What it is**: financial OS for ag + trades. Bookkeeping + receipt-scan-by-AI + bill
  pay + team cards + inventory + per-enterprise P&L. Optional full-service bookkeeper
  add-on.
- **ICP**: small-mid farms, ranches, contractors. Multi-enterprise (e.g., row crop +
  livestock + custom-haul as separate P&Ls under one business).
- **Positioning**: _"Financial tools worthy of your work."_ Rural Americana aesthetic —
  warm photography of actual operators, paired with sharp UI. Authenticity-first; this
  is the brand farm-pack has to look at if/when we build a marketing site.
- **Where it overlaps farm-pack**: bookkeeping, bill pay, enterprise P&L (≈ Odoo
  analytic accounts + farm-pack tagging).
- **Where it doesn't**: production records (fields/crops/plantings/harvests), geo (no
  maps), CSA/delivery routes, online storefront, observation capture in the field, USDA
  overlays.

### Traction Ag — `tractionag.com`

- _Page returned 403; profile below is from general industry knowledge — verify before
  quoting publicly._
- **What it is**: row-crop farm ERP. Accounting + grain marketing + AP/AR
  - payroll + equipment/asset tracking. QuickBooks migration on-ramp.
- **ICP**: larger row-crop farms (often 1,000+ acres, Iowa/Illinois belt).
- **Positioning**: serious accounting for serious row-crop operators — positioned as
  "QuickBooks for real farms."
- **Where it overlaps farm-pack**: accounting + QBO sync + payroll + asset/equipment.
- **Where it doesn't**: direct-to-consumer commerce, CSA, delivery routes,
  observation/scouting, geo overlays for compliance.

### FarmRaise — `farmraise.com`

- **What it is**: "system of record for farm data." Mobile-first farm records +
  financial planning + payroll + grant/program management + field-trial data collection.
  Capture once, reuse across reports.
- **ICP**: farmers/ranchers managing finances; program administrators running USDA/NRCS
  grants; researchers running trials.
- **Positioning**: standardize farm data to kill duplicate entry across stakeholders
  (farmer → grant admin → researcher). Mobile-first.
- **Where it overlaps farm-pack**: financial planning + records + payroll, plus the same
  urge to centralize data.
- **Where it doesn't**: storefront, online ordering, CSA contracts, weekly delivery
  routing, geo/USDA overlays at parcel level. Their strength is the grant/program
  reporting flow that farm-pack does not address at all.

### FieldEdge — `fieldedge.com`

- **What it is**: field service management — dispatch, scheduling, mobile tech,
  invoicing, QuickBooks/Intacct sync.
- **ICP**: HVAC + plumbing contractors. _Not a farm product._
- **Why it's on the radar**: structurally close to what farm-pack's "weekly delivery
  routes" job needs — recurring routes, mobile driver app, optimized dispatch, QBO sync.
  We can borrow shape from FSM vendors without competing with them.
- **Where it overlaps farm-pack**: route + dispatch + driver mobile.
- **Where it doesn't**: production records, ecommerce, ag-specific workflows
  (variable-weight billing, CSA shares).

### Agritecture article — `agritecture.com/blog/farm-to-doorstep-delivery-logistics`

- Not a product. A thinkpiece arguing D2C farms need integrated tooling rather than
  patched stacks. Useful as **positioning ammunition**.
- Six categories the article lists as essential for D2C ag: storefront, route
  optimization + GPS, subscription/standing-order management, payments (incl. SNAP/EBT),
  driver mobile, invoicing/accounting.
- Pain points called out:
  - Fragmented stacks, manual re-entry across systems.
  - Generic GPS apps can't handle delivery windows + perishables.
  - **Variable-weight billing** (e.g. half-share of beef arrives 47.3 lb not 50.0 lb)
    breaking flat-price invoicing.
  - Customers having to email/call to pause subscriptions.
- **farm-pack covers**: storefront, ordering, weekly routes, accounting/QBO. **farm-pack
  does NOT yet cover**: variable-weight reconciliation, SNAP/EBT, customer-self-service
  subscription pause/skip, driver mobile app.

### UW-Extension reviewer — `farms.extension.wisc.edu`

- Not a product. An extension-service buyer's-guide page. Names the category leaders
  that real farmers compare against: **Quicken, QuickBooks, CenterPoint Accounting for
  Agriculture, EasyFarm, Farm Biz / Ultra Farm, PcMars** + Excel templates from Cornell,
  Missouri, Michigan State.
- Selection criteria the extension uses: features offered, support (phone/online), cost,
  reports for management decisions.
- **Useful for farm-pack**: this is the list our QBO-import on-ramp has to make
  migrating _easier_ than it would be to switch to. The big two we have to move people
  off of are QuickBooks and Quicken — CenterPoint is the prosumer ag-specific option to
  position against.

## Where farm-pack fits

Map of who-eats-what; farm-pack lives where no single competitor ranges across all four
bands at once for the SMB segment.

```
                  bookkeeping   production    commerce      logistics
                  +finances     records       +storefront   +routing
                  =========     ==========    ==========    ==========
QuickBooks/Quicken    ✅           ❌            ❌            ❌
CenterPoint Ag        ✅           ◐ (basic)     ❌            ❌
Ambrook               ✅✅         ◐ (inv only)  ❌            ❌
Traction Ag           ✅✅         ✅ (rowcrop)  ❌            ❌
FarmRaise             ✅           ✅            ❌            ❌
FieldEdge             ◐ (sync)     ❌            ❌            ✅ (FSM)
Shopify + plugins     ❌           ❌            ✅✅          ◐
farm-pack (this)      ✅ (QBO IO)  ✅            ✅            ✅
```

## Implications for positioning + roadmap

1. **Wedge sentence drafts** (all to be A/B'd, not committed yet):
   - _"The farm app that doesn't make you pick between accounting and online sales."_
   - _"From Facebook posts and Venmo to a CSA-ready storefront in 10 minutes."_
     (homestead tier — already in the project memory)
   - _"QuickBooks-compatible, Schedule F-ready, route-aware. One install."_ (SMB tier)
2. **Visual brand reference**: Ambrook is the bar — rural-Americana photography + sharp
   UI. We should NOT default to a generic SaaS purple-gradient look. Aesthetic direction
   for the eventual marketing page is closer to **editorial / farm-trade-journal** than
   to dev-tools.
3. **Feature gaps worth fast-following**:
   - Variable-weight billing on delivery (Agritecture pain point; concrete win for
     direct beef/produce sales).
   - Customer-self-service subscription pause/skip in the portal.
   - Receipt-scan / OCR on bills (Ambrook's table stakes — Odoo has
     `account_invoice_extract` upstream, wire it into `farm_pack`).
   - SNAP/EBT acceptance flow — research-only for now, regulatory.
4. **Don't chase**:
   - Grant/program reporting (FarmRaise's moat; out of our four-jobs scope).
   - Grain-marketing modules (Traction Ag's row-crop specialization).
   - HVAC-style dispatch board (FieldEdge's vertical; our routes are weekly recurring,
     not on-demand service calls).
5. **Migration story**: the UW-Extension list tells us the import paths that matter —
   Quicken QIF, QuickBooks IIF/QBO, CenterPoint CSV. Today `farm_quickbooks_io` covers
   the second; the others are candidates if anyone asks during partner conversations.

## What's _not_ in this file (deliberately deferred)

- Pricing intelligence — none of the public pages list prices; would need partner-call
  notes or trial signups.
- Screenshot library of each competitor's UI for visual benchmarking — do once we have a
  positioning page draft and need design references.
- Interview notes from the 50-east-coast-farms research (task #19 completed; raw notes
  live outside this repo).
