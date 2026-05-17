Adds PostGIS polygon boundaries to `farm.field` and auto-computes acreage
from the geometry.

Without this module, `farm.field.acres` is a manual decimal entry. With it,
draw a polygon on a Leaflet map and the acreage updates from the polygon area
(reprojected to EPSG:5070 Albers Equal Area, the projection NRCS and NASS use
for the lower 48).

The base `farm_field` module remains usable without PostGIS — install this
extension only when your deployment has a PostGIS-enabled Postgres.
