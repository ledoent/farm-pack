from odoo import api, fields, models


class FarmDeliveryRoute(models.Model):
    _name = "farm.delivery.route"
    _description = "Delivery Route"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_date desc, name"
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    scheduled_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    driver_id = fields.Many2one(
        "res.users",
        string="Driver",
        tracking=True,
        default=lambda self: self.env.user,
    )
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="planned",
        required=True,
        tracking=True,
    )
    stop_ids = fields.One2many(
        "farm.route.stop",
        "route_id",
        copy=True,
    )
    stop_count = fields.Integer(compute="_compute_stop_count")
    note = fields.Html()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends("stop_ids")
    def _compute_stop_count(self):
        for route in self:
            route.stop_count = len(route.stop_ids)

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_complete(self):
        self.write({"state": "completed"})
        for route in self:
            route.stop_ids.filtered(lambda s: s.state == "pending").write(
                {"state": "delivered"}
            )

    def action_cancel(self):
        self.write({"state": "cancelled"})


class FarmRouteStop(models.Model):
    _name = "farm.route.stop"
    _description = "Route Stop"
    _order = "route_id, sequence, id"

    route_id = fields.Many2one(
        "farm.delivery.route",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    dropoff_point_id = fields.Many2one(
        "farm.dropoff.point",
        required=True,
        tracking=True,
    )
    partner_id = fields.Many2one(related="dropoff_point_id.partner_id", store=True)
    address = fields.Char(related="dropoff_point_id.address", readonly=True)
    instructions = fields.Text(related="dropoff_point_id.instructions", readonly=True)
    package_count = fields.Integer(default=1, help="Number of boxes/items to leave.")
    note = fields.Char(help="Stop-specific note overriding the dropoff default.")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("delivered", "Delivered"),
            ("skipped", "Skipped"),
        ],
        default="pending",
        required=True,
    )

    def action_mark_delivered(self):
        self.write({"state": "delivered"})

    def action_mark_skipped(self):
        self.write({"state": "skipped"})
