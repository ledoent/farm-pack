# Farm GEO modules — implementation plan

Builds on the research at
`/Users/dkendall/projects/ledoent/oca/reports/farm-geo-mapping-stack.md`. Three phases
(MVP / v1 / v2), six modules. Each module is independently installable and tested; later
phases compose on earlier ones.

## Dependencies

All confirmed available on `OCA/geospatial` 19.0 branch:

| Module                               | What it provides                                                                                                                                                                            |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `base_geoengine`                     | PostGIS column types (`GeoPolygon`, `GeoLineString`, `GeoPoint`, `GeoMultiPolygon`), Leaflet widget, projection helpers (WGS84 ↔ Web Mercator ↔ Albers Equal Area for US acreage compute) |
| `web_leaflet_draw_lib`               | Leaflet-Geoman wrapper for in-form polygon editing                                                                                                                                          |
| `base_geoengine_geocoder` (optional) | Nominatim address → centroid for "I don't know the polygon yet" partner fallback                                                                                                            |

Workspace `repos.yaml` already pins `./geospatial`. PostGIS auto-enables in
postgres:16-postgis (Docker image swap when we wire this in).

## Module decomposition

```
farm_field                (MVP)  — fields as polygons + acreage + crop catalog
farm_field_overlays       (MVP)  — USDA CDL + NRCS SSURGO read-only layers
farm_observation          (v1)   — geotagged photos + timestamped notes
farm_water_source         (v1)   — wells / ponds / streams / troughs
farm_fence                (v1)   — fence linestrings + condition tracking
farm_field_mobile         (v2)   — PWA service-worker for offline capture
```

`farm_pack` umbrella picks up `farm_field` + `farm_field_overlays` at MVP; v1 modules
added when they ship.

---

## Phase 1 — MVP (one focused session)

### `farm_field`

**Purpose:** polygons-as-fields with crop catalog + acreage compute.

**Files**

```
farm_field/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   └── farm_field.py
├── data/
│   └── farm_field_crop_data.xml      ← 30-ish common crops, seeded
├── security/ir.model.access.csv
├── views/
│   ├── farm_field_views.xml          ← list + kanban + form + geoengine map
│   └── farm_field_menu.xml
├── demo/
│   └── farm_field_demo.xml           ← 4 demo polygons around the demo farm
├── tests/
│   ├── __init__.py
│   └── test_farm_field.py
└── readme/{DESCRIPTION,USAGE,CONTRIBUTORS}.md + newsfragments/.gitkeep
```

**Manifest depends:** `farm_base`, `base_geoengine`, `web_leaflet_draw_lib`

**Models**

```python
class FarmField(models.Model):
    _name = "farm.field"
    _description = "Farm Field / Plot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    farm_partner_id = fields.Many2one("res.partner", string="Farm", required=True)
    company_id = fields.Many2one("res.company", required=True,
                                 default=lambda self: self.env.company, index=True)
    geom = fields.GeoPolygon(string="Boundary", srid=4326)
    acres = fields.Float(compute="_compute_acres", store=True, digits=(8, 2),
                         help="Computed from geometry area, reprojected to "
                              "EPSG:5070 (Albers Equal Area) for accurate US acreage.")
    crop_id = fields.Many2one("farm.field.crop", string="Current Crop")
    crop_year = fields.Integer(default=lambda self: fields.Date.today().year)
    organic_certified = fields.Boolean(tracking=True)
    notes = fields.Html()
    active = fields.Boolean(default=True)
    season_id = fields.Many2one("farm.season")  # from farm_base

    @api.depends("geom")
    def _compute_acres(self):
        # base_geoengine helper reprojects + computes area
        # m^2 → acres = m^2 / 4046.8564224
        for rec in self:
            if not rec.geom:
                rec.acres = 0.0
                continue
            m2 = rec.geom.transform(5070).area
            rec.acres = m2 / 4046.8564224

class FarmFieldCrop(models.Model):
    _name = "farm.field.crop"
    _description = "Crop Catalog"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(default=0)              # for map coloring
    code = fields.Char()                            # e.g. "CORN", "SOY01", USDA-CDL-compatible
    is_perennial = fields.Boolean(help="Tree fruit, hay, pasture — multi-year")
    is_organic_eligible = fields.Boolean()
```

**Crop seed (30 records):** corn, soybean, wheat, oats, alfalfa, mixed hay, pasture,
sweet corn, tomato, pepper, lettuce, kale, herbs (mixed), strawberry, blueberry,
raspberry, apple, peach, pumpkin, squash, garlic, onion, potato, carrot, radish, fallow,
cover crop (mixed), buckwheat, sunflower, sorghum.

**Views**

- **Kanban** — card per field showing name + crop_id (colored) + acres + small
  static-image preview of polygon
- **List** — name, crop, acres, organic_certified, season
- **Form** — header with active/archive; sheet has name + farm_partner_id + crop_id +
  crop_year + organic_certified; notebook tabs: Boundary (geoengine map widget for
  in-form drawing/edit), Notes
- **Geoengine view** — full-screen map showing all fields colored by crop (using
  `crop_id.color`); click-to-open field form
- **Menu** — Farm → Fields → Fields (list/kanban), Farm → Fields → Map (geoengine), Farm
  → Configuration → Crop Catalog

**Demo data**

4 polygons drawn around `partner_demo_alice` / `partner_demo_bob` from the existing
demo:

- "North 40" — 40 acres corn (CDL color: yellow)
- "South Pasture" — 25 acres pasture (green)
- "East Garden" — 2 acres mixed vegetables (red)
- "Berry Hill" — 5 acres strawberry (pink)

Drawn as approximate polygons around the Ligonier PA centroid (40.2421°N, 79.2389°W).

**Tests**

- `test_acres_compute_from_geom` — known polygon → assert acres within 0.1 of expected
- `test_acres_zero_when_no_geom` — null geometry → 0 acres
- `test_field_crud` — create / update geometry / archive
- `test_geometry_srid_normalisation` — input WGS84 round-trips correctly

### `farm_field_overlays`

**Purpose:** read-only public-domain layers toggleable on the field map.

**Files**

```
farm_field_overlays/
├── __manifest__.py                    ← depends: farm_field
├── __init__.py
├── data/
│   └── overlay_config.xml             ← ir.config_parameter entries for layer URLs
├── views/
│   └── farm_field_geoengine_layers.xml  ← extends the map view to add layer toggles
└── readme/...
```

**Layer URLs (ir.config_parameter)**

```
farm.geo.overlay.cdl_url       = https://gis.apfo.usda.gov/arcgis/rest/services/...
farm.geo.overlay.ssurgo_url    = https://sdmdataaccess.nrcs.usda.gov/ArcGIS/...
farm.geo.overlay.nhd_url       = https://hydro.nationalmap.gov/arcgis/...
farm.geo.overlay.topo_url      = https://services.nationalmap.gov/arcgis/...
```

(Final URLs locked when implementing — verify each is currently serving.)

**Tests:** smoke render with one layer enabled; assert the WMS URL ends up in the
rendered map config.

### MVP wiring

- Add `farm_field` + `farm_field_overlays` to `farm_pack/__manifest__.py` depends
- Add to `farm_pack_demo/__manifest__.py` demo data list (demo polygons file)
- Update workspace `addons.yaml` to list both new modules

### MVP CI

Standard OCA workflow already covers it. Smoke locally first:

```
./scripts/preflight.sh
cd /Users/dkendall/projects/ledoent/oca/industry-packs
invoke install -m farm_field
invoke test farm_field
```

### MVP verification

1. `/web#action=farm_field.action_field_kanban` shows 4 demo fields with crop badges
2. Click a field → form opens with boundary already drawn (Leaflet-Geoman edit mode)
3. Drag a vertex → save → `acres` field updates within ±1% of original
4. Switch to map view (geoengine) → see all 4 fields colored by crop
5. Toggle "USDA Cropland 2025" overlay → see CDL crop coloring beneath the polygons
6. Toggle SSURGO Soil → see soil-type polygons beneath

---

## Phase 2 — v1 (next session)

### `farm_observation`

**Purpose:** geotagged photos + timestamped notes, urgency-sorted.

```python
class FarmObservation(models.Model):
    _name = "farm.observation"
    _description = "Field Observation"
    _inherit = ["mail.thread"]
    _order = "observation_date desc, urgency desc"

    field_id = fields.Many2one("farm.field", required=True, index=True)
    name = fields.Char(compute="_compute_name", store=True)
    observation_type = fields.Selection([
        ("pest", "Pest Damage"),
        ("disease", "Disease"),
        ("weed", "Weed Pressure"),
        ("soil", "Soil Condition"),
        ("water", "Water / Drainage"),
        ("yield", "Yield Issue"),
        ("photo", "Photo Survey"),
        ("other", "Other"),
    ], required=True, default="photo")
    geom = fields.GeoPoint(srid=4326)          # auto-pop from photo EXIF if present
    observation_date = fields.Datetime(required=True, default=fields.Datetime.now)
    notes = fields.Text(required=True)
    photo_id = fields.Many2one("ir.attachment", domain="[('mimetype', 'ilike', 'image/')]")
    urgency = fields.Selection([
        ("low", "Low"),
        ("med", "Medium"),
        ("high", "High"),
    ], default="low", tracking=True)
```

**Views:** kanban (cards with photo thumbnail + urgency badge + age), list (sortable by
urgency + date), form with photo upload + map widget for point picking.

**EXIF extraction:** small JS helper on the form view's photo upload — reads GPS tags,
auto-sets `geom`.

### `farm_water_source`

```python
class FarmWaterSource(models.Model):
    _name = "farm.water.source"
    _description = "Water Source"

    name = fields.Char(required=True)
    source_type = fields.Selection([
        ("well", "Well"),
        ("tank", "Surface Tank"),
        ("pond", "Pond"),
        ("stream", "Stream / Creek"),
        ("trough", "Trough"),
        ("spring", "Spring"),
        ("hydrant", "Hydrant / Spigot"),
    ], required=True)
    geom = fields.GeoMultiGeometry()            # base_geoengine union type
    field_ids = fields.Many2many("farm.field", help="Fields served by this source")
    capacity_gallons = fields.Float()
    last_tested_date = fields.Date()
    quality_notes = fields.Text()
    active = fields.Boolean(default=True)
```

Conditional geometry: well/trough/spring/hydrant = point; stream = linestring; pond/tank
= polygon. `GeoMultiGeometry` lets one field hold any of those.

### `farm_fence`

```python
class FarmFence(models.Model):
    _name = "farm.fence"
    _description = "Fence"

    name = fields.Char(required=True)
    field_id = fields.Many2one("farm.field")    # primary field; can be null if perimeter
    geom = fields.GeoLineString(srid=4326)
    length_feet = fields.Float(compute="_compute_length_feet", store=True)
    fence_type = fields.Selection([
        ("barbed_wire", "Barbed Wire"),
        ("high_tensile", "High-Tensile"),
        ("electric", "Electric"),
        ("post_rail", "Post & Rail"),
        ("woven_wire", "Woven Wire"),
        ("polywire", "Polywire (rotational)"),
        ("temporary", "Temporary"),
    ], required=True)
    height_inches = fields.Float()
    condition = fields.Selection([
        ("good", "Good"),
        ("fair", "Fair"),
        ("repair", "Needs Repair"),
    ], default="good", tracking=True)
    last_checked_date = fields.Date()
    notes = fields.Text()
```

Length compute mirrors acres compute on `farm_field`.

### v1 wiring

- Add all three to `farm_pack` depends + `farm_pack_demo` demo data + workspace
  `addons.yaml`
- Demo: 6 observations (mix of types), 2 water sources (a well + a pond), 3 fences
  (perimeter, paddock divider, garden enclosure)

---

## Phase 3 — v2 (separate session, only if needed)

### `farm_field_mobile`

PWA bundle for offline observation + field-edit capture. Real engineering — defer until
a design partner asks. Sketch:

- Service worker (Workbox) caches `/farm_field/*`, `/farm_observation/*` routes and base
  map tiles
- IndexedDB queue for offline observation creates / photo uploads
- "Sync now" button polls when online; batches POSTs via Odoo RPC
- Bottom-tab mobile UI (separate website snippet) replacing the back-office form views
  for field operators
- Photo capture uses `<input type="file" accept="image/*" capture="environment">` +
  `exif-js` for GPS tags

Out of scope until: (a) at least one design partner explicitly says they need offline,
AND (b) field-test confirms 4G coverage is the bottleneck (often it isn't — observers
come back to the farmhouse, sync there).

---

## What's deliberately NOT in scope

- **Mapbox Satellite tiles** — commercial license; use free OpenStreetMap + USGS aerial
  via `base_geoengine` default base layers
- **John Deere Operations Center / Climate FieldView OAuth ingestion** — proprietary
  customer data; light up as separate modules `farm_field_jd_sync` +
  `farm_field_fieldview_sync` only when a customer asks
- **Native iOS / Android apps** — PWA covers the 90% case; native only on demand
- **3D / elevation modeling** — beyond MVP scope; could come later as
  `farm_field_terrain`

---

## Risks

| Risk                                                            | Mitigation                                                                                                                                                                |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OCA/geospatial` 19.0 modules unstable or unpublished as wheels | Pre-flight check: `pip --dry-run install` each one before depending. If unavailable, mark our `farm_field` `installable:False` like we did with `farm_csa_contract_glue`. |
| USDA / NRCS / USGS WMS endpoints change URLs                    | URLs are ir.config_parameter; documented procedure to swap. Add a smoke check in CI that pings each one.                                                                  |
| Acreage compute miscalibrates between WGS84 and Albers          | Test with known-good US polygon (USDA-published parcel area). Reject deviations >1%.                                                                                      |
| PostGIS dependency bloats deploy footprint                      | Switch the workspace Docker image to `postgis/postgis:16-3.4-alpine` (only ~5MB larger). Tested already in OCA reference deployments.                                     |
| Leaflet-Geoman has a license boundary at 100 features per map   | Confirmed free for non-commercial OR open-source AGPL-3 use (our case). Pin the version in package.json.                                                                  |

---

## Implementation order

When you give the green light to start:

1. Add `postgis/postgis:16-3.4` to workspace `common.yaml` (`db` service)
2. Verify `OCA/geospatial` modules install:
   `invoke install -m base_geoengine,web_leaflet_draw_lib`
3. Scaffold `farm_field/` via the OCA module template (mirror existing modules'
   structure)
4. Write models + views + crop seed + 4 demo polygons
5. Pre-commit + tests local; push; CI verifies
6. Scaffold `farm_field_overlays/` once `farm_field` is green
7. Update `farm_pack` umbrella manifest + `farm_pack_demo` demo data
8. Update workspace `addons.yaml`
9. Hand-test on the dev container: visit the map, draw a field, save, verify acreage
10. Surface for design-partner review

Total estimate: 1 focused session for `farm_field`, 1 for `farm_field_overlays`, 2 for
the v1 trio. v2 PWA is a separate ~2-session block.
