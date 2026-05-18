from odoo import api, fields, models


class FarmHarvest(models.Model):
    _name = "farm.harvest"
    _description = "Farm Harvest"
    _inherit = ["farm.mixin"]
    _order = "harvest_date desc, id desc"
    _check_company_auto = True

    name = fields.Char(compute="_compute_name", store=True, precompute=True)
    planting_id = fields.Many2one(
        "farm.planting",
        string="Planting",
        ondelete="set null",
        help="Optional. When set, field + crop auto-fill from the planting on "
        "create. Clearing it later does NOT clear field/crop (manual record).",
    )
    field_id = fields.Many2one(
        "farm.field",
        string="Field",
        required=True,
        ondelete="restrict",
        check_company=True,
        compute="_compute_field_crop",
        store=True,
        readonly=False,
        precompute=True,
        tracking=True,
    )
    crop_id = fields.Many2one(
        "farm.crop",
        string="Crop",
        required=True,
        ondelete="restrict",
        compute="_compute_field_crop",
        store=True,
        readonly=False,
        precompute=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        related="field_id.company_id",
        store=True,
        index=True,
        precompute=True,
    )
    harvest_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    qty_harvested = fields.Float(digits=(12, 3), required=True, tracking=True)
    qty_uom_id = fields.Many2one("uom.uom", string="UoM", required=True)
    season_id = fields.Many2one(
        "farm.season",
        related="field_id.season_id",
        store=True,
        readonly=False,
    )
    grade = fields.Selection(
        [
            ("a", "A (premium)"),
            ("b", "B (seconds)"),
            ("c", "C (utility)"),
            ("compost", "Compost"),
        ],
        help="Optional quality grade for tiered pricing.",
    )

    @api.depends("planting_id")
    def _compute_field_crop(self):
        for rec in self:
            if rec.planting_id:
                rec.field_id = rec.planting_id.field_id
                rec.crop_id = rec.planting_id.crop_id

    @api.depends("qty_harvested", "qty_uom_id", "crop_id", "harvest_date")
    def _compute_name(self):
        for rec in self:
            bits = []
            if rec.qty_harvested:
                bits.append(f"{rec.qty_harvested:g}")
            if rec.qty_uom_id:
                bits.append(rec.qty_uom_id.name)
            if rec.crop_id:
                bits.append(rec.crop_id.name)
            if rec.harvest_date:
                bits.append(f"on {rec.harvest_date.isoformat()}")
            rec.name = " ".join(bits) or self.env._("New Harvest")
