**Farm → Plantings** captures what got planted where. Pick a field, pick a crop,
set the date. Expected harvest auto-fills from `crop.days_to_maturity` (override
freely).

The state buttons walk a planting through its lifecycle:

- **Mark Growing** — once seedlings emerge / direct seed germinates
- **Mark Harvested** (highlighted) — once the last pick is in (`farm.harvest`
  records track individual picks)
- **Mark Failed** — pest, weather, etc.

Filter by state, group by field or crop, color-code attention items via the
kanban color.
