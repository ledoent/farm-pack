Heavy demo dataset for the farm pack. Installs on top of `farm_pack` and
populates:

- **9 partners**: 6 retail customers, 3 wholesale/drop-off accounts (Boyd's
  Wellness Pantry, Saturday Market, Corner Store Co-Op), 3 vendors
- **8 products**: 2 egg SKUs (dozen / half-dozen), 3 produce items, 2 CSA
  shares (Small / Family Weekly), 1 value-added (berry jam) — all published
  on the website
- **2 coops** (Back, Garden) with 5+ days of egg collection history each
- **2 CSA tiers** + **3 active subscriptions** in different payment states
  (paid-ahead / current / owes), plus last week's delivered boxes and this
  week's drafts
- **5 drop-off points** + **1 Tuesday delivery route** with 4 stops
- **1 demo QBO connection** in sandbox mode — pull works via the stub
  fixture without real Intuit credentials

Designed so a fresh `odoo --init=farm_pack,farm_pack_demo` lands on a
working site with realistic data ready for partner demos and Playwright
tests.
