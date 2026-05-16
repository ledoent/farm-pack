1. Install `farm_pack_demo` for sample data — you'll get a "Saturday
   Farmers Market" event in `preorder_open` state with offerings.
2. Visit `/market` on your website. The upcoming market is listed.
3. Click into the market → see offerings as cards with quantity + Preorder
   buttons.
4. Set a quantity, click **Preorder** → product is added to cart with
   carrier_id = Market Pickup. The cart's `farm_market_event_id`
   auto-resolves via the carrier's next-upcoming-open-event compute.
5. Proceed through `/shop/cart` and `/shop/checkout` like any other Odoo
   e-commerce order.
6. Back-office: the new sale order shows up under the event's Preorders
   tab. **Pick List — What to Bring** aggregates the customer's quantity
   into the truck load-out.
