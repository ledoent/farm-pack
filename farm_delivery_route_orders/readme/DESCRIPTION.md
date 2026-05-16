**Composition-first replacement** for the custom `farm_delivery_routes`
module. Instead of paralleling Odoo's batch-picking primitive with a
bespoke route + stop model, this module:

- Adds `farm_delivery_date` and `farm_delivery_zone_id` to `sale.order`
  (and propagates them to `stock.picking` so the wizard can filter on them)
- Provides a `farm.delivery.zone` lookup table (6 default zones seeded:
  Farm Pickup, Market, North, South, East, West)
- Ships a **Build Weekly Route** wizard that selects confirmed outgoing
  pickings by date + zone and rolls them into a `stock.picking.batch`
- Extends the batch view with the route date + zone + stop count

The batch becomes the driver's pick-list: Odoo's native UI shows the
pickings, the operator drags to reorder, prints the picking-batch report,
and marks the batch done — no custom UI required.

`farm_delivery_routes` (the custom version shipped earlier) stays
installable in this release for data continuity; v2 deprecates it.
