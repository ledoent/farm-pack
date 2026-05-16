from odoo import fields, models


class FarmDropoffPoint(models.Model):
    _name = "farm.dropoff.point"
    _description = "Drop-Off Point"
    _inherit = ["mail.thread", "farm.gps.point.mixin"]
    _order = "name"
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    kind = fields.Selection(
        [
            ("home", "Home / Porch"),
            ("market", "Farmers Market"),
            ("pantry", "Pantry / Co-Op"),
            ("workplace", "Workplace"),
            ("other", "Other"),
        ],
        default="home",
        required=True,
        tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        help="Contact person at this drop-off (host, manager, etc.). Optional.",
    )
    address = fields.Char(
        help="Free-text address. Map widget arrives in v1 with base_geoengine.",
    )
    instructions = fields.Text(
        help="Free text: 'leave in cooler on porch', 'gate code 1234', "
        "'ask for Sarah at the booth', etc.",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    stop_ids = fields.One2many("farm.route.stop", "dropoff_point_id")
    stop_count = fields.Integer(compute="_compute_stop_count")

    def _compute_stop_count(self):
        Stop = self.env["farm.route.stop"]
        data = Stop._read_group(
            [("dropoff_point_id", "in", self.ids)],
            ["dropoff_point_id"],
            ["__count"],
        )
        counts = {dp.id: count for dp, count in data}
        for point in self:
            point.stop_count = counts.get(point.id, 0)
