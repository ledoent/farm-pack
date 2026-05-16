from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    farm_market_event_id = fields.Many2one(
        "event.event",
        string="Farm Market (pickup at)",
        domain="[('is_farm_market', '=', True)]",
        tracking=True,
        help="If set, this order is a preorder for pickup at this farmers "
        "market event. Aggregated into the day-of pick list.",
    )
    farm_market_state = fields.Selection(
        related="farm_market_event_id.farm_market_state", store=True
    )

    @api.constrains("farm_market_event_id", "state")
    def _check_preorder_cutoff(self):
        for order in self:
            event = order.farm_market_event_id
            if not event:
                continue
            if event.farm_market_state in ("preorder_closed", "live", "closed") and (
                order.state in ("draft", "sent")
            ):
                raise ValidationError(
                    self.env._(
                        "Preorders for %(event)s are closed. The order cannot be "
                        "created or modified.",
                        event=event.name,
                    )
                )
