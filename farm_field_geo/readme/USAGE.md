1. Open Farm → Fields → Fields and pick a field.
2. The **Boundary** notebook tab renders a Leaflet map of the field's polygon.
3. Set the polygon via the geoengine map view (vertex drag works there) or by
   importing a WKT string. In-form vertex editing through the boundary tab
   arrives once `web_leaflet_draw_lib` is migrated to Odoo 19.
4. Save. The **Acres** field auto-recomputes from the polygon area, reprojected
   to EPSG:5070 Albers Equal Area.
5. Switch the action's view to **Map** (geoengine) to see every field at once.

The `acres` field stays editable as a fallback: fields without a digitized
boundary can carry a manual estimate. Once a polygon is set, the compute
overrides the manual value.

Multi-plot fields (a "north 40" that is two non-contiguous polygons) need
`GeoMultiPolygon` rather than `GeoPolygon` — out of scope for the MVP;
record each plot as its own `farm.field` for now.
