Manage CSA (Community-Supported Agriculture) memberships for homestead and
small farm operations:

- `farm.csa.tier` — share offerings (Small Weekly $25, Family Bi-Weekly $50,
  etc.) tied to a `product.product` for downstream invoicing
- `farm.csa.subscription` — one member's standing order; tracks dates,
  delivery method (pickup farm / market / drop-off / home delivery), payment
  status (paid-ahead / current / owes — a lightweight off-system marker for
  Venmo-style cash flow)
- `farm.csa.box` — one delivery for one subscription, with a flat list of
  contents; calendar view to plan the week, state machine drafted →
  packed → delivered

Intentionally not coupled to OCA `contract` or Odoo subscription billing in
MVP — homesteaders run on Venmo, not enterprise invoicing. The
`product_id` on the tier lets you bolt on standard sale-order invoicing later
without restructuring.
