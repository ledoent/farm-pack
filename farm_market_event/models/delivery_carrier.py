from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    is_farm_market_pickup = fields.Boolean(
        string="Farm Market Pickup",
        help="This shipping method represents pickup at a recurring farmers "
        "market series (e.g. 'Saturday Farmers Market - Town Square'). "
        "Each weekly instance is a separate event.event record; the "
        "carrier stays stable so customer preferences and recurring orders "
        "don't break when the next event is created.",
    )
    farm_market_event_ids = fields.One2many(
        "event.event",
        "farm_market_carrier_id",
        string="Market Events",
    )
    farm_market_next_event_id = fields.Many2one(
        "event.event",
        compute="_compute_farm_market_next_event_id",
        string="Next Market",
        help="Next upcoming market in this series that is accepting preorders.",
    )

    @api.depends(
        "farm_market_event_ids.farm_market_state",
        "farm_market_event_ids.date_begin",
    )
    def _compute_farm_market_next_event_id(self):
        now = fields.Datetime.now()
        for carrier in self:
            events = carrier.farm_market_event_ids.filtered(
                lambda e: (
                    e.farm_market_state == "preorder_open"
                    and (not e.date_begin or e.date_begin >= now)
                )
            ).sorted("date_begin")
            carrier.farm_market_next_event_id = events[:1]
