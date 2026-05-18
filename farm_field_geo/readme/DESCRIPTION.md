Adds PostGIS polygon boundaries to `farm.field` and auto-computes acreage
from the geometry.

Without this module, `farm.field.acres` is a manual decimal entry. With it,
set a WGS84 polygon as the field's boundary and the acreage updates from the
polygon area, reprojected to EPSG:5070 (Conus Albers Equal Area) — the
projection NRCS and NASS use for lower-48 area calculations, so the number
matches what soil-survey and yield tooling would report for the same parcel.

`acres` remains editable as a fallback: fields without a digitized boundary
keep working with a manual estimate, and the compute only fires once a
polygon is set.

**Scope.** This module ships a single `GeoPolygon` per field — non-contiguous
plots (two disconnected polygons that are administratively one "field")
should be recorded as separate `farm.field` records for now. A future
`farm_field_multi_polygon` extension can promote the column to
`GeoMultiPolygon` if the demand materializes.

**Install requirement.** The Postgres instance must have PostGIS enabled.
`base_geoengine` declares the extension; install will fail cleanly if the
extension is missing. The base `farm_field` module stays usable without
PostGIS — install this extension only when geometry support is wanted.
