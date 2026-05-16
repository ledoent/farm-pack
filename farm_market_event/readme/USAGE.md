1. **Farm → Markets → Farmers Markets**: create the event. Set date/time,
   location, mark **Farm Market**, set the **Preorder Cutoff**.
2. On the event form, **Farm Market** tab: add `farm.market.offering` rows
   — one per product (eggs, tomatoes, jam, etc.) with `max_qty` and price.
3. Click **Open Preorders**. Share the event link / signup form with your
   list. Each preorder is a sale order with `farm_market_event_id` set.
4. As preorders come in, `preorder_qty` and `available_qty` on each
   offering update in real time. The header **Committed Revenue** number
   tells you how much money is already in the bag.
5. At the cutoff, click **Close Preorders**. The pickup time is
   approaching; this prevents new orders.
6. Click **Pick List — What to Bring** (or print the PDF report from the
   event action menu). Load the truck.
7. **Go Live** when you arrive at the booth. Walk-up sales flow as plain
   `sale.order` records.
8. **Close Market** when you pack up. Done.
