1. Open Farm → Fields → Fields and pick a field.
2. On the form, the **Boundary** field renders a Leaflet map.
3. Draw the field perimeter as a polygon (read-only viewer for now; in-form
   drawing arrives once `web_leaflet_draw_lib` is migrated to Odoo 19).
4. Save. The **Acres** field auto-recomputes from the polygon area.
5. Switch the action's view to **Map** to see every field on one canvas.
