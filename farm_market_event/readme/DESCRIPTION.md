Farmers markets modelled as **events with preorder-for-pickup**, the
Eventbrite/Luma pattern applied to farm-stand reality.

The fundamental insight from the UX research: a Saturday farmers market is
not a storefront, it's an event. It has a start window, a location, a
capacity (booth size + how much a vehicle can haul), and an in-season /
sold-out cycle that plays out across the morning. Eventbrite, Luma, and
Manage My Market all model this well; CSA-space tools don't.

**Composition:** sits on top of Odoo CE `event` + `sale_management`. Adds
the farm-market overlay; no new event engine.

**Key models:**
- Extends `event.event` with `is_farm_market`, `preorder_cutoff_datetime`,
  and a 5-state machine (`planning → preorder_open → preorder_closed →
  live → closed`)
- `farm.market.offering` — one row per (event, product) with `max_qty`
  (how many you can bring), `list_price` (per-event override), and
  computed `preorder_qty` / `available_qty`
- Extends `sale.order` with `farm_market_event_id` so a preorder is just
  a sale order linked to the event. Constraint rejects new preorders once
  state ≥ `preorder_closed`.

**The pick-list workflow:**
1. Create the event, flip `is_farm_market`, add `farm.market.offering` rows
2. Open preorders → customers preorder eggs/tomatoes/etc. for pickup
3. Cutoff hits → close preorders → click **Pick List — What to Bring**
4. Wizard aggregates preorder qty per product + recommends 1.5× buffer for
   walk-up sales (capped at planned max)
5. Print the PDF pick list — that's literally the load-out for the truck
6. Go Live → during market, walk-up sales flow as normal sale orders
7. Close Market — done.
