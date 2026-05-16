from odoo import fields, models
from odoo.exceptions import UserError


class FarmWeeklyRouteWizard(models.TransientModel):
    _name = "farm.weekly.route.wizard"
    _description = "Build a Weekly Delivery Route from confirmed orders"

    delivery_date = fields.Date(required=True, default=fields.Date.context_today)
    delivery_zone_id = fields.Many2one("farm.delivery.zone")
    driver_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, required=True
    )
    picking_ids = fields.Many2many(
        "stock.picking",
        compute="_compute_picking_ids",
    )

    def _domain(self):
        domain = [
            ("state", "in", ("assigned", "confirmed", "waiting")),
            ("picking_type_code", "=", "outgoing"),
            ("farm_delivery_date", "=", self.delivery_date),
            ("batch_id", "=", False),
        ]
        if self.delivery_zone_id:
            domain.append(("farm_delivery_zone_id", "=", self.delivery_zone_id.id))
        return domain

    def _compute_picking_ids(self):
        for wiz in self:
            if not wiz.delivery_date:
                wiz.picking_ids = self.env["stock.picking"]
                continue
            wiz.picking_ids = self.env["stock.picking"].search(wiz._domain())

    def action_build_route(self):
        self.ensure_one()
        pickings = self.env["stock.picking"].search(self._domain())
        if not pickings:
            raise UserError(
                self.env._(
                    "No outgoing pickings match this date and zone — nothing to batch."
                )
            )
        batch = self.env["stock.picking.batch"].create(
            {
                "user_id": self.driver_id.id,
                "farm_delivery_date": self.delivery_date,
                "farm_delivery_zone_id": self.delivery_zone_id.id or False,
                "picking_ids": [(6, 0, pickings.ids)],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking.batch",
            "res_id": batch.id,
            "view_mode": "form",
            "target": "current",
        }
