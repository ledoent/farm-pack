from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FarmEggCollection(models.Model):
    _name = "farm.egg.collection"
    _description = "Egg Collection"
    _inherit = ["mail.thread"]
    _order = "collection_date desc, id desc"
    _check_company_auto = True

    name = fields.Char(compute="_compute_name", store=True)
    collection_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    coop_id = fields.Many2one(
        "farm.coop",
        required=True,
        ondelete="restrict",
        tracking=True,
        check_company=True,
    )
    count_total = fields.Integer(
        string="Total Collected",
        required=True,
        tracking=True,
        help="Total eggs collected today including broken/cracked.",
    )
    count_broken = fields.Integer(
        string="Broken / Cracked",
        default=0,
        help="Eggs collected but unsellable due to damage.",
    )
    count_kept_home = fields.Integer(
        string="Kept for Home",
        default=0,
        help="Eggs kept by the household and never offered for sale.",
    )
    count_available = fields.Integer(
        compute="_compute_count_available",
        store=True,
        help="Eggs available for sale or gifting: total minus broken minus kept-home.",
    )
    note = fields.Char(
        help="Optional one-liner for the day (weather, hen health, etc.)."
    )
    company_id = fields.Many2one(
        related="coop_id.company_id",
        store=True,
        index=True,
    )

    _count_total_non_negative = models.Constraint(
        "CHECK (count_total >= 0)",
        "Total egg count cannot be negative.",
    )
    _count_broken_non_negative = models.Constraint(
        "CHECK (count_broken >= 0)",
        "Broken egg count cannot be negative.",
    )
    _count_kept_home_non_negative = models.Constraint(
        "CHECK (count_kept_home >= 0)",
        "Eggs-kept-home count cannot be negative.",
    )
    _one_per_coop_per_day = models.Constraint(
        "UNIQUE (coop_id, collection_date)",
        "Only one egg collection record per coop per day.",
    )

    @api.depends("count_total", "count_broken", "count_kept_home")
    def _compute_count_available(self):
        for rec in self:
            rec.count_available = max(
                0, rec.count_total - rec.count_broken - rec.count_kept_home
            )

    @api.depends("coop_id", "collection_date", "count_total")
    def _compute_name(self):
        for rec in self:
            if rec.coop_id and rec.collection_date:
                rec.name = (
                    f"{rec.coop_id.name} · {rec.collection_date} · {rec.count_total}"
                )
            else:
                rec.name = self.env._("Draft Collection")

    @api.constrains("count_total", "count_broken", "count_kept_home")
    def _check_subcounts_within_total(self):
        for rec in self:
            if rec.count_broken + rec.count_kept_home > rec.count_total:
                raise ValidationError(
                    self.env._(
                        "Broken (%(broken)s) + kept-home (%(kept)s) cannot exceed "
                        "total collected (%(total)s).",
                        broken=rec.count_broken,
                        kept=rec.count_kept_home,
                        total=rec.count_total,
                    )
                )
