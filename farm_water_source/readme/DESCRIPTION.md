Tracks water sources on the farm — wells, surface tanks, ponds, streams,
troughs, springs, hydrants — with their location, capacity, last-tested
date, and which fields they serve.

The `geom` column uses `GeoMultiGeometry` so one field can hold any of:

- **Point** — well, trough, spring, hydrant (single coordinate)
- **LineString** — stream / creek (multi-segment path)
- **Polygon** — pond / surface tank (closed area)

The trade-off is looser shape validation in exchange for not needing four
separate models. Conventional usage matches each `source_type` to a shape,
documented in USAGE; an admin who wants strict per-type validation can
layer a `_constraint` on top later.

The `field_ids` many2many answers "which fields does this source serve?",
useful when planning rotational grazing or drought contingency.
