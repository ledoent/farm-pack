Public preorder pages for farmers market events. Without this module the
preorder flow only exists in the back-office; customers can't self-serve.

Routes:
- `/market` — lists upcoming markets accepting preorders
- `/market/<event_id>` — detail page with offering cards + quantity-aware
  "Preorder" buttons (only rendered when `farm_market_state ==
  'preorder_open'`)
- `/market/<event_id>/preorder` — POST handler that adds the offering's
  product to the visitor's cart and sets `carrier_id` to the event's
  market series carrier. The cart's `farm_market_event_id` auto-resolves
  via the existing `farm_market_event` compute.

After preorder, the visitor lands on the standard `/shop/cart` page and
proceeds through Odoo's normal checkout — single payment flow, single set
of invoices.

Depends on `website_sale` (the cart + checkout primitive) and
`farm_market_event` (data model + carrier-as-series).
