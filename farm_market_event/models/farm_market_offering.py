from odoo import api, fields, models


class FarmMarketOffering(models.Model):
    _name = "farm.market.offering"
    _description = "Product available at a Farm Market event"
    _order = "event_id, sequence, id"

    event_id = fields.Many2one(
        "event.event",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('is_farm_market', '=', True)]",
    )
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product", required=True, domain=[("sale_ok", "=", True)]
    )
    max_qty = fields.Float(
        string="Max Available",
        default=0.0,
        help="How many units you can bring to this market. 0 = unlimited.",
    )
    list_price = fields.Monetary(
        currency_field="currency_id",
        help="Override the product's list price for this event (leave 0 to use "
        "the product default).",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    preorder_qty = fields.Float(
        compute="_compute_preorder_qty",
        help="Total quantity preordered for this product at this event.",
    )
    available_qty = fields.Float(
        compute="_compute_available_qty",
        help="Remaining qty available for preorder. Negative means over-committed.",
    )

    @api.depends("event_id.farm_preorder_ids.order_line.product_uom_qty", "product_id")
    def _compute_preorder_qty(self):
        for rec in self:
            if not rec.event_id or not rec.product_id:
                rec.preorder_qty = 0.0
                continue
            product = rec.product_id
            preorder_lines = (
                rec.event_id.farm_preorder_ids.filtered(
                    lambda o: o.state in ("sale", "done", "draft", "sent")
                )
                .mapped("order_line")
                .filtered(lambda line, p=product: line.product_id == p)
            )
            rec.preorder_qty = sum(preorder_lines.mapped("product_uom_qty"))

    @api.depends("max_qty", "preorder_qty")
    def _compute_available_qty(self):
        for rec in self:
            if rec.max_qty == 0:
                rec.available_qty = -1  # sentinel for "unlimited"
            else:
                rec.available_qty = rec.max_qty - rec.preorder_qty
