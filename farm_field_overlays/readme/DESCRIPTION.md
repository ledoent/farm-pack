Adds three public-domain US-government overlay layers to the farm field map:

- **OpenStreetMap** — basemap; roads, parcels, buildings (default visible)
- **USDA Cropland (CDL)** — current-year crop-classification raster covering
  the lower 48; overlays the historical crop on a farmer's parcels so you can
  see what was planted in previous years from satellite-derived
  classification (50%-opacity by default)
- **NRCS SSURGO Soil** — soil mapunit polygons; click-through gives soil
  type, drainage class, productivity (40%-opacity by default)

All three are read-only: no API keys, no per-request quota, no proprietary
data. Layers are stored as `geoengine.raster.layer` records bound to the
field map view, so an admin can disable, reorder, or edit the WMS endpoints
via Settings → Technical → Geoengine → Raster Layers without touching code.

**Scope.** Read-only display only. Click-to-query (e.g. "what soil type is
under this point?") needs a `farm_field_query` follow-up module that wires
up GetFeatureInfo round-trips. USGS NHD (hydrography) and Topo are deferred
to a follow-up to keep this PR tight.
