Geotagged field observations: timestamped notes + a photo + a point on the
map, urgency-sorted so the high-priority items rise to the top of every
list and kanban.

Each observation belongs to a `farm.field` and carries:

- **Type** — pest damage, disease, weed pressure, soil condition, water,
  yield issue, photo survey, other
- **Urgency** — low / medium / high (tracked via mail.thread so a manager
  sees who bumped it and when)
- **Location** — optional `GeoPoint` you set by clicking the map widget on
  the Location tab
- **Photo** — a single representative attachment; use chatter for additional
  shots
- **Notes** — required free text

Views: list (color-coded by urgency), urgency-grouped kanban, form with
chatter, search with last-7-days + high-urgency canned filters, and a
geoengine map view that drops pins on the field map.

**Scope.** Manual point-picking only. Auto-population from photo EXIF GPS
tags is deferred — needs an OWL JS helper on the photo upload widget that
parses the file client-side. Track in a follow-up if a field partner asks.
