Farmers markets modelled as **events with preorder-for-pickup**, the
Eventbrite/Luma pattern applied to farm-stand reality.

The fundamental insight from the UX research: a Saturday farmers market is
not a storefront, it's an event. It has a start window, a location, a
capacity (booth size + how much a vehicle can haul), and an in-season /
sold-out cycle that plays out across the morning. Eventbrite, Luma, and
Manage My Market all model this well; CSA-space tools don't.

**Composition:** sits on top of Odoo CE `event` + `sale_management` +
`delivery`. Adds the farm-market overlay; no new event engine.

**Key insight on data model:** the recurring market is the stable concept;
each weekly instance has a fresh `event.event` ID. To avoid customer
preferences pointing at stale event IDs:

- The **`delivery.carrier`** (Saturday Market Pickup) is the *series* —
  stable across weeks, picked once and forgotten by the customer
- The **`event.event`** is one *instance* of that series, churning weekly
- `sale.order.farm_market_event_id` is **computed**, not directly set —
  derives from the carrier's next-upcoming-open event

**Key models:**
- Extends `delivery.carrier` with `is_farm_market_pickup` flag and a
  computed `farm_market_next_event_id` (next upcoming preorder-open event
  in this series)
- Extends `event.event` with `is_farm_market`, `farm_market_carrier_id`
  (back-link to the series), `preorder_cutoff_datetime`, and a 5-state
  machine (`planning → preorder_open → preorder_closed → live → closed`)
- `farm.market.offering` — one row per (event, product) with `max_qty`
  (how many you can bring), `list_price` (per-event override), and
  computed `preorder_qty` / `available_qty`
- Extends `sale.order` with `farm_market_event_id` **computed** from the
  chosen carrier. Constraint rejects new preorders once the resolved
  event's state ≥ `preorder_closed`.

**The pick-list workflow:**
1. Create the event, flip `is_farm_market`, add `farm.market.offering` rows
2. Open preorders → customers preorder eggs/tomatoes/etc. for pickup
3. Cutoff hits → close preorders → click **Pick List — What to Bring**
4. Wizard aggregates preorder qty per product + recommends 1.5× buffer for
   walk-up sales (capped at planned max)
5. Print the PDF pick list — that's literally the load-out for the truck
6. Go Live → during market, walk-up sales flow as normal sale orders
7. Close Market — done.
