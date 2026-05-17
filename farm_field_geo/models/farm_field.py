from odoo import api, fields, models

# Square meters in one US survey acre. Used to convert EPSG:5070 area
# (Albers Equal Area, units = m^2) to acres.
M2_PER_ACRE = 4046.8564224

# Conus Albers Equal Area — the projection NRCS and USDA use for area
# calculations across the lower 48. We reproject the WGS84 polygon to 5070
# before measuring area so the number matches what soil-survey and NASS
# tooling would report for the same parcel.
ALBERS_CONUS_SRID = 5070


class FarmField(models.Model):
    _inherit = "farm.field"

    geom = fields.GeoPolygon(
        string="Boundary",
        srid=4326,
        help="Field boundary as a WGS84 polygon. Drives the computed acreage; "
        "stored as PostGIS geometry.",
    )
    acres = fields.Float(
        compute="_compute_acres_from_geom",
        store=True,
        readonly=False,
        digits=(8, 2),
        help="Auto-computed from the polygon area when a boundary is drawn. "
        "Editable as a fallback for fields without a digitized boundary yet.",
    )

    @api.depends("geom")
    def _compute_acres_from_geom(self):
        for rec in self:
            if not rec.geom:
                continue
            rec.acres = rec.geom.transform(ALBERS_CONUS_SRID).area / M2_PER_ACRE
