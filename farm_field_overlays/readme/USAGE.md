1. Open Farm → Fields → Fields and switch to the **Map** view.
2. The layer toggle (top-right of the map) lists OpenStreetMap, USDA Cropland,
   and NRCS Soil. Toggle each on/off independently.
3. To customize a layer (URL, opacity, ordering): Settings → Technical →
   Geoengine → Raster Layers — pick the layer, edit, save.

**Annual update — USDA CDL.** The Cropland Data Layer is published per
crop year and the WMS layer name carries the year (e.g. `cdl_2024`).
USDA typically publishes the new year's raster in Feb/Mar of the following
calendar year. Each January or February, update the LAYERS param on the
"USDA Cropland" raster layer record:

1. Settings → Technical → Geoengine → Raster Layers → "USDA Cropland (CDL …)"
2. Edit Params WMS, change `cdl_YYYY` to the new year
3. Update the layer's display name to match
4. Save and reload the map view

To add another WMS overlay (e.g. USGS NHD hydrography for streams + ponds):

1. Settings → Technical → Geoengine → Raster Layers → New
2. Raster layer type: **Distant WMS**
3. URL: the WMS endpoint
4. Params WMS: `{"LAYERS": "<layer-name>", "FORMAT": "image/png", "TRANSPARENT": "TRUE"}`
5. Bind to view: **farm.field.geoengine**
6. Save; reload the map view.
