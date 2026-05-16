from odoo import api, fields, models


class FarmCsaSubscription(models.Model):
    _name = "farm.csa.subscription"
    _description = "CSA Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, partner_id"
    _check_company_auto = True

    name = fields.Char(compute="_compute_name", store=True)
    partner_id = fields.Many2one(
        "res.partner", required=True, tracking=True, index=True
    )
    tier_id = fields.Many2one("farm.csa.tier", required=True, tracking=True)
    date_start = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True
    )
    date_end = fields.Date(tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("cancelled", "Cancelled"),
            ("expired", "Expired"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    payment_status = fields.Selection(
        [
            ("paid_ahead", "Paid Ahead"),
            ("current", "Current"),
            ("owes", "Owes"),
        ],
        default="current",
        tracking=True,
        help="Lightweight payment status — homesteaders track this off-system "
        "(Venmo, cash). Update by hand or via downstream invoicing.",
    )
    delivery_method = fields.Selection(
        [
            ("pickup_farm", "Pickup at Farm"),
            ("pickup_market", "Farmers Market"),
            ("delivery", "Home Delivery"),
            ("dropoff", "Drop-Off Point"),
        ],
        default="pickup_farm",
        required=True,
    )
    delivery_notes = fields.Char(
        help="Free text: 'leave in cooler on porch, gate code 1234', etc."
    )
    box_ids = fields.One2many("farm.csa.box", "subscription_id")
    box_count = fields.Integer(compute="_compute_box_count")
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends("partner_id", "tier_id", "date_start")
    def _compute_name(self):
        for sub in self:
            if sub.partner_id and sub.tier_id:
                sub.name = f"{sub.partner_id.name} · {sub.tier_id.name}"
            else:
                sub.name = self.env._("New CSA Subscription")

    @api.depends("box_ids")
    def _compute_box_count(self):
        for sub in self:
            sub.box_count = len(sub.box_ids)

    def action_activate(self):
        self.write({"state": "active"})

    def action_pause(self):
        self.write({"state": "paused"})

    def action_cancel(self):
        self.write({"state": "cancelled"})
