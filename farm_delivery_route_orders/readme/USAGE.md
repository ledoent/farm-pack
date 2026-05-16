1. **Farm → Configuration → Delivery Zones**: define your geographic zones
   (default six are pre-loaded).
2. On each **Sale Order**, set the **Delivery Date** and **Delivery Zone**
   alongside the existing date_order field.
3. Confirm the order — picking inherits the date + zone via stored
   `related` fields.
4. **Farm → Order Routes → Build Weekly Route**: pick a date and zone, see
   matching pickings as a preview, click **Build Route**. The wizard
   creates a `stock.picking.batch` and opens it.
5. From the batch, use Odoo's native batch-picking flow: drag to reorder
   stops, print the pick-list report, mark each picking delivered, then
   mark the batch done.
