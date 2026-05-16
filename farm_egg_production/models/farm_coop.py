from odoo import api, fields, models


class FarmCoop(models.Model):
    _name = "farm.coop"
    _description = "Coop"
    _inherit = ["mail.thread", "farm.gps.point.mixin"]
    _order = "name"
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    capacity = fields.Integer(
        help="Maximum number of birds the coop is rated for.",
    )
    active_bird_count = fields.Integer(
        string="Bird Count",
        default=0,
        tracking=True,
        help="Current head count of birds in this coop.",
    )
    note = fields.Html()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)

    collection_ids = fields.One2many(
        "farm.egg.collection", "coop_id", string="Collections"
    )
    eggs_last_7_days = fields.Integer(
        compute="_compute_eggs_last_7_days",
        help="Total eggs collected over the last 7 days, useful for spotting drops.",
    )

    @api.depends("collection_ids.count_total", "collection_ids.collection_date")
    def _compute_eggs_last_7_days(self):
        Collection = self.env["farm.egg.collection"]
        cutoff = fields.Date.subtract(fields.Date.context_today(self), days=7)
        for coop in self:
            recent = Collection.search(
                [("coop_id", "=", coop.id), ("collection_date", ">=", cutoff)]
            )
            coop.eggs_last_7_days = sum(recent.mapped("count_total"))
