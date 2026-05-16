from odoo import fields, models


class FarmCsaTier(models.Model):
    _name = "farm.csa.tier"
    _description = "CSA Share Tier"
    _order = "sequence, price_per_period"

    name = fields.Char(required=True, help="e.g. 'Small Weekly', 'Family Bi-Weekly'.")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("sale_ok", "=", True)],
        help="Product used when generating invoices for this tier.",
    )
    cadence = fields.Selection(
        [
            ("weekly", "Weekly"),
            ("biweekly", "Bi-Weekly"),
            ("monthly", "Monthly"),
        ],
        default="weekly",
        required=True,
    )
    price_per_period = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    description = fields.Html(help="What a member at this tier gets each delivery.")
    active = fields.Boolean(default=True)
    subscription_count = fields.Integer(
        compute="_compute_subscription_count",
    )

    def _compute_subscription_count(self):
        Subscription = self.env["farm.csa.subscription"]
        data = Subscription._read_group(
            [("tier_id", "in", self.ids), ("state", "=", "active")],
            ["tier_id"],
            ["__count"],
        )
        counts = {tier.id: count for tier, count in data}
        for tier in self:
            tier.subscription_count = counts.get(tier.id, 0)
