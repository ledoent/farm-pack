from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    farm_delivery_date = fields.Date(
        string="Route Delivery Date",
        help="Target date for the customer to receive their order. Used by "
        "the weekly route wizard to group orders into a batch picking. "
        "Distinct from sale.order.commitment_date which already has the "
        "'Delivery Date' label.",
        tracking=True,
    )
    farm_delivery_zone_id = fields.Many2one(
        "farm.delivery.zone",
        string="Delivery Zone",
        tracking=True,
    )

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_default_zone(self):
        for order in self:
            if (
                order.partner_shipping_id
                and not order.farm_delivery_zone_id
                and "farm_delivery_zone_id" in order.partner_shipping_id._fields
            ):
                order.farm_delivery_zone_id = (
                    order.partner_shipping_id.farm_delivery_zone_id
                )
