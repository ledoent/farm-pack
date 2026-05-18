Tracks water sources on the farm — wells, surface tanks, ponds, streams,
troughs, springs, hydrants — with their location, capacity, last-tested
date, and which fields they serve.

The `geom` column is a `GeoPoint`. All source types are represented as a
single point: the well-head, the tank tap, the centroid of the pond, the
access point on the stream. We picked this in v1 because base_geoengine
19.0 doesn't ship a "any geometry" type — adding a polygon footprint for
ponds (surface-area, depth contours) or a linestring for streams would
need a follow-up `farm_water_source_polygon` extension model.

The `field_ids` many2many answers "which fields does this source serve?",
useful when planning rotational grazing or drought contingency.
