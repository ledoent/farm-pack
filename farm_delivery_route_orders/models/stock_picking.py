from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    farm_delivery_date = fields.Date(
        related="sale_id.farm_delivery_date", store=True, index=True
    )
    farm_delivery_zone_id = fields.Many2one(
        "farm.delivery.zone",
        related="sale_id.farm_delivery_zone_id",
        store=True,
        index=True,
    )
