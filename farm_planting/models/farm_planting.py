from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FarmPlanting(models.Model):
    _name = "farm.planting"
    _description = "Farm Planting"
    _inherit = ["farm.mixin"]
    _order = "plant_date desc, id desc"
    _check_company_auto = True

    name = fields.Char(
        compute="_compute_name",
        store=True,
        precompute=True,
    )
    field_id = fields.Many2one(
        "farm.field",
        string="Field",
        required=True,
        ondelete="restrict",
        check_company=True,
        tracking=True,
    )
    crop_id = fields.Many2one(
        "farm.crop",
        string="Crop",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    company_id = fields.Many2one(
        related="field_id.company_id",
        store=True,
        index=True,
        precompute=True,
    )
    plant_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    expected_harvest_date = fields.Date(
        compute="_compute_expected_harvest_date",
        store=True,
        readonly=False,
        help="Defaults to plant_date + crop.days_to_maturity. Override freely.",
    )
    qty_seeded = fields.Float(
        digits=(12, 3),
        help="Quantity seeded — units for transplants, lb/oz for seed weight.",
    )
    qty_uom_id = fields.Many2one("uom.uom", string="UoM")
    season_id = fields.Many2one(
        "farm.season",
        related="field_id.season_id",
        store=True,
        readonly=False,
    )
    state = fields.Selection(
        [
            ("planted", "Planted"),
            ("growing", "Growing"),
            ("harvested", "Harvested"),
            ("failed", "Failed"),
        ],
        default="planted",
        required=True,
        tracking=True,
    )

    @api.depends("crop_id", "field_id", "plant_date")
    def _compute_name(self):
        for rec in self:
            if rec.crop_id and rec.field_id and rec.plant_date:
                rec.name = (
                    f"{rec.crop_id.name} on {rec.field_id.name}"
                    f" ({rec.plant_date.isoformat()})"
                )
            else:
                rec.name = self.env._("New Planting")

    @api.depends("plant_date", "crop_id")
    def _compute_expected_harvest_date(self):
        for rec in self:
            if rec.plant_date and rec.crop_id and rec.crop_id.days_to_maturity:
                rec.expected_harvest_date = rec.plant_date + timedelta(
                    days=rec.crop_id.days_to_maturity
                )

    @api.constrains("plant_date", "expected_harvest_date")
    def _check_dates(self):
        for rec in self:
            if (
                rec.expected_harvest_date
                and rec.plant_date
                and rec.expected_harvest_date < rec.plant_date
            ):
                raise ValidationError(
                    self.env._(
                        "Expected harvest date can't be before plant date "
                        "(%(p)s → %(h)s).",
                        p=rec.plant_date,
                        h=rec.expected_harvest_date,
                    )
                )

    def action_mark_growing(self):
        self.write({"state": "growing"})

    def action_mark_harvested(self):
        self.write({"state": "harvested"})

    def action_mark_failed(self):
        self.write({"state": "failed"})
