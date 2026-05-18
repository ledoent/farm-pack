from functools import lru_cache

from pyproj import Transformer
from shapely.ops import transform as shapely_transform

from odoo import api, fields, models

# US survey foot in meters. Used to convert EPSG:5070 length (m) to feet
# for display — US farm fencing is universally specified in feet.
M_PER_US_SURVEY_FOOT = 0.3048006096012192


@lru_cache(maxsize=1)
def _wgs84_to_albers_conus():
    """Build the EPSG:4326 → EPSG:5070 transformer once and reuse it.

    Same approach farm_field_geo uses for acreage — Albers reprojection
    gives a length number that matches what NRCS reports for the same
    fence in a rangeland-improvement filing.
    """
    return Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True).transform


class FarmFence(models.Model):
    _name = "farm.fence"
    _description = "Fence"
    _inherit = ["mail.thread", "farm.rank.mixin"]
    # Repairs-needed bubble to the top. `rank` comes from farm.rank.mixin
    # (mirrors `condition` through the selection→int map below so DESC
    # sort gives repair > fair > good instead of alpha-DESC's broken order).
    _order = "rank desc, name"
    # Enforces field_id.company_id == fence.company_id at write time (only
    # checked when field_id is set; perimeter fences with a null field_id
    # pass through).
    _check_company_auto = True
    # farm.rank.mixin wiring:
    _rank_selection_field = "condition"
    _rank_value_map = {"good": 0, "fair": 1, "repair": 2}

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(
        default=True,
        help="Untick to archive fences that have been removed or replaced. "
        "Their geometry and history stay on the field map's archived view.",
    )
    field_id = fields.Many2one(
        "farm.field",
        string="Primary Field",
        help="Field this fence belongs to. Leave blank for perimeter fences "
        "that span multiple fields.",
        ondelete="set null",
        check_company=True,
    )
    geom = fields.GeoLine(
        string="Fence Line",
        srid=4326,
        help="Polyline tracing the fence. Length and the map view come from "
        "this geometry. base_geoengine 19.0 names the type GeoLine (no "
        "'String' suffix).",
    )
    length_feet = fields.Float(
        compute="_compute_length_feet",
        store=True,
        digits=(10, 1),
        help="Auto-computed from the polyline length, reprojected to "
        "EPSG:5070 (Albers Equal Area) and converted from meters to US "
        "survey feet.",
    )
    fence_type = fields.Selection(
        [
            ("barbed_wire", "Barbed Wire"),
            ("high_tensile", "High-Tensile"),
            ("electric", "Electric"),
            ("post_rail", "Post & Rail"),
            ("woven_wire", "Woven Wire"),
            ("polywire", "Polywire (rotational)"),
            ("temporary", "Temporary"),
        ],
        required=True,
        tracking=True,
    )
    height_inches = fields.Float(digits=(5, 1))
    condition = fields.Selection(
        [
            ("good", "Good"),
            ("fair", "Fair"),
            ("repair", "Needs Repair"),
        ],
        default="good",
        required=True,
        tracking=True,
    )
    last_checked_date = fields.Date(tracking=True)
    notes = fields.Text()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends("geom")
    def _compute_length_feet(self):
        # base_geoengine returns the field as a plain shapely geometry on
        # read; shapely has no .transform() method. Reproject via pyproj +
        # shapely.ops.transform before measuring length. Mirrors the
        # acreage compute in farm_field_geo.
        transformer = _wgs84_to_albers_conus()
        for rec in self:
            if not rec.geom:
                rec.length_feet = 0.0
                continue
            projected = shapely_transform(transformer, rec.geom)
            rec.length_feet = projected.length / M_PER_US_SURVEY_FOOT
