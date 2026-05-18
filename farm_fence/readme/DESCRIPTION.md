Tracks fence lines on the farm with type (barbed wire, high-tensile,
electric, post-and-rail, woven wire, polywire, temporary), height,
condition (good / fair / needs repair), last-checked date, and an
auto-computed length in feet from the polyline geometry.

`length_feet` mirrors the acreage compute in `farm_field_geo`: the
WGS84 polyline is reprojected to **EPSG:5070 Conus Albers Equal Area**
and the geodesic length in meters is converted to US survey feet
(0.3048006096012192 m/ft). The number matches what NRCS would report
for the same fence line in a rangeland improvement filing.

Repairs-needed bubble to the top of every list and grouped kanban
because `_order` uses a stored computed `condition_rank` integer
mirroring the selection — a naive string DESC would put "good" above
"fair" (alpha order).

Field link is optional (`ondelete="set null"`) so a perimeter fence
spanning multiple fields keeps its history even when one field is
archived or deleted.
