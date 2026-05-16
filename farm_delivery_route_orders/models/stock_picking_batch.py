from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    farm_delivery_date = fields.Date(
        string="Route Date",
        help="The delivery date this route covers.",
    )
    farm_delivery_zone_id = fields.Many2one(
        "farm.delivery.zone",
        string="Zone",
    )
    farm_stop_count = fields.Integer(compute="_compute_farm_stop_count")

    def _compute_farm_stop_count(self):
        for rec in self:
            rec.farm_stop_count = len(rec.picking_ids)
