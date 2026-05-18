from odoo import api, fields, models

# US survey foot in meters. Used to convert EPSG:5070 length (m) to feet
# for display — US farm fencing is universally specified in feet.
M_PER_US_SURVEY_FOOT = 0.3048006096012192

# Same Conus Albers projection farm_field_geo uses for acreage, applied to
# fence linestrings for length. Reprojecting before measuring keeps the
# number consistent with how NRCS reports rangeland improvements.
ALBERS_CONUS_SRID = 5070

# Selection keys are descriptive strings (good/fair/repair) for the UI, but
# alpha-DESC would order "repair > good > fair" — fair-condition fences
# would hide below good-condition ones. `condition_rank` mirrors the
# selection so `_order` produces the actual urgency sort.
_CONDITION_RANK = {"good": 0, "fair": 1, "repair": 2}


class FarmFence(models.Model):
    _name = "farm.fence"
    _description = "Fence"
    _inherit = ["mail.thread"]
    # Repairs-needed bubble to the top.
    _order = "condition_rank desc, name"
    # Enforces field_id.company_id == fence.company_id at write time (only
    # checked when field_id is set; perimeter fences with a null field_id
    # pass through).
    _check_company_auto = True

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
    geom = fields.GeoLineString(
        string="Fence Line",
        srid=4326,
        help="Polyline tracing the fence. Length and the map view come from "
        "this geometry.",
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
    condition_rank = fields.Integer(
        compute="_compute_condition_rank",
        store=True,
        index=True,
        help="Numeric mirror of condition so _order produces an urgency sort "
        "(string DESC on selection keys would put 'good' above 'fair').",
    )
    last_checked_date = fields.Date(tracking=True)
    notes = fields.Text()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends("condition")
    def _compute_condition_rank(self):
        for rec in self:
            rec.condition_rank = _CONDITION_RANK.get(rec.condition, 0)

    @api.depends("geom")
    def _compute_length_feet(self):
        for rec in self:
            if not rec.geom:
                rec.length_feet = 0.0
                continue
            meters = rec.geom.transform(ALBERS_CONUS_SRID).length
            rec.length_feet = meters / M_PER_US_SURVEY_FOOT
