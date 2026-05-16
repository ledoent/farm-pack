from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    farm_market_event_id = fields.Many2one(
        "event.event",
        string="Farm Market (pickup at)",
        compute="_compute_farm_market_event_id",
        store=True,
        index=True,
        tracking=True,
        help="The specific market event this preorder is routed to. Computed "
        "from the chosen carrier's next upcoming open event — never set "
        "directly, because event IDs change every week as new events are "
        "created. The carrier is the stable concept.",
    )
    farm_market_state = fields.Selection(
        related="farm_market_event_id.farm_market_state", store=True
    )

    @api.depends("carrier_id", "carrier_id.farm_market_next_event_id")
    def _compute_farm_market_event_id(self):
        for order in self:
            if order.carrier_id.is_farm_market_pickup:
                order.farm_market_event_id = order.carrier_id.farm_market_next_event_id
            else:
                order.farm_market_event_id = False

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
