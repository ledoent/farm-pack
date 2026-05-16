from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    is_farm_market = fields.Boolean(
        string="Farm Market",
        help="Treat this event as a farmers market: enables product offerings, "
        "preorders for pickup, and the 'what to bring' pick list.",
    )
    preorder_cutoff_datetime = fields.Datetime(
        string="Preorder Cutoff",
        help="When preorders close. After this moment new preorders are rejected, "
        "but the farmer can still aggregate the existing pick list and bring "
        "extra for walk-up sales.",
    )
    farm_market_state = fields.Selection(
        [
            ("planning", "Planning"),
            ("preorder_open", "Preorder Open"),
            ("preorder_closed", "Preorder Closed — Setting Up"),
            ("live", "Live at Market"),
            ("closed", "Closed"),
        ],
        default="planning",
        tracking=True,
    )
    farm_offering_ids = fields.One2many(
        "farm.market.offering", "event_id", string="Product Offerings"
    )
    farm_offering_count = fields.Integer(compute="_compute_farm_offering_count")
    farm_preorder_ids = fields.One2many(
        "sale.order", "farm_market_event_id", string="Preorders"
    )
    farm_preorder_count = fields.Integer(compute="_compute_farm_preorder_count")
    farm_preorder_revenue = fields.Monetary(
        compute="_compute_farm_preorder_revenue",
        currency_field="currency_id",
        help="Total committed-money from confirmed preorders for this market.",
    )

    @api.depends("farm_offering_ids")
    def _compute_farm_offering_count(self):
        for rec in self:
            rec.farm_offering_count = len(rec.farm_offering_ids)

    @api.depends("farm_preorder_ids")
    def _compute_farm_preorder_count(self):
        for rec in self:
            rec.farm_preorder_count = len(rec.farm_preorder_ids)

    @api.depends("farm_preorder_ids.amount_total", "farm_preorder_ids.state")
    def _compute_farm_preorder_revenue(self):
        for rec in self:
            confirmed = rec.farm_preorder_ids.filtered(
                lambda o: o.state in ("sale", "done")
            )
            rec.farm_preorder_revenue = sum(confirmed.mapped("amount_total"))

    def action_open_preorders(self):
        self.write({"farm_market_state": "preorder_open"})

    def action_close_preorders(self):
        self.write({"farm_market_state": "preorder_closed"})

    def action_go_live(self):
        self.write({"farm_market_state": "live"})

    def action_close_market(self):
        self.write({"farm_market_state": "closed"})

    def action_open_picklist_wizard(self):
        self.ensure_one()
        wizard = self.env["farm.market.picklist.wizard"].create({"event_id": self.id})
        return {
            "type": "ir.actions.act_window",
            "res_model": "farm.market.picklist.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }
