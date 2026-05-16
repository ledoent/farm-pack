Shared foundation for the [farm pack](https://github.com/ledoent/farm-pack).
Provides:

- `farm.season` — the time period plantings, harvests, and herd movements roll up into
- `farm.measurement.mixin` — abstract mixin for any model carrying a value + unit pair
- `farm.gps.point.mixin` — abstract mixin for optional WGS84 lat/lon
- Agricultural units of measure: bushels (corn / soybean / wheat), hundredweight,
  US ton, acre, hectare, head

This module holds no business logic and is never installed standalone — it exists so
the leaf farm modules can share types without diamond dependencies.
