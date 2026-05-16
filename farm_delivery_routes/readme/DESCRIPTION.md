Plan and execute weekly delivery routes for homestead operators:

- `farm.dropoff.point` — a place to leave a box (porch, pantry, market
  booth, workplace) with instructions and optional contact partner. Inherits
  `farm.gps.point.mixin` for optional WGS84 coordinates.
- `farm.delivery.route` — one route on one day: driver, ordered stops,
  state machine (planned → in_progress → completed). Cancelling a route
  is non-destructive.
- `farm.route.stop` — a stop on a route, referencing a drop-off point and
  carrying a package count + per-stop note. Stops can be individually
  marked delivered/skipped; finishing the route auto-delivers any stops
  still pending.
