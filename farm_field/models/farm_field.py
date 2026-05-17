from odoo import fields, models


class FarmField(models.Model):
    _name = "farm.field"
    _description = "Farm Field"
    _inherit = ["farm.mixin"]
    _order = "name"
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short code used on signage, planting tags, harvest sheets "
        "(e.g. 'N-12' for North 12-acre).",
    )
    farm_partner_id = fields.Many2one(
        "res.partner",
        string="Farm",
        domain="[('is_company','=',True)]",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    acres = fields.Float(
        digits=(8, 2),
        help="Manual entry until the GEO pack lands and recomputes from polygon.",
    )
    crop_id = fields.Many2one(
        "farm.crop",
        string="Current Crop",
        tracking=True,
        help="What's planted on this field right now. Use farm.planting for "
        "multi-season history.",
    )
    season_id = fields.Many2one("farm.season")
    organic_certified = fields.Boolean(tracking=True)

    # NOTE: GEO fields (geom, computed acres from polygon) land in farm_field_geo
    # as an extension so this base lives without PostGIS.
