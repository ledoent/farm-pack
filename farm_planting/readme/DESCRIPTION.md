Planting events: a crop went into a field on a date. Records what was planted,
how much, expected harvest date (auto-computed from `crop.days_to_maturity`),
and tracks state through planning → planted → growing → harvested (or failed).

Used by `farm_harvest` to link a harvest record back to the planting that
produced it (and indirectly: field + crop + season).
