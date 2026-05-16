from odoo import api, fields, models


class FarmCsaBox(models.Model):
    _name = "farm.csa.box"
    _description = "CSA Box (one delivery)"
    _inherit = ["mail.thread"]
    _order = "delivery_date desc, partner_id"

    name = fields.Char(compute="_compute_name", store=True)
    subscription_id = fields.Many2one(
        "farm.csa.subscription",
        required=True,
        ondelete="cascade",
        index=True,
    )
    partner_id = fields.Many2one(related="subscription_id.partner_id", store=True)
    delivery_date = fields.Date(required=True, tracking=True)
    delivery_method = fields.Selection(
        related="subscription_id.delivery_method", store=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("packed", "Packed"),
            ("delivered", "Delivered"),
            ("missed", "Missed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("farm.csa.box.line", "box_id")
    line_count = fields.Integer(compute="_compute_line_count")
    note = fields.Char(help="Note specific to this delivery, e.g. 'extra basil'.")

    @api.depends("partner_id", "delivery_date")
    def _compute_name(self):
        for box in self:
            if box.partner_id and box.delivery_date:
                box.name = f"{box.partner_id.name} · {box.delivery_date}"
            else:
                box.name = self.env._("New Box")

    @api.depends("line_ids")
    def _compute_line_count(self):
        for box in self:
            box.line_count = len(box.line_ids)

    def action_mark_packed(self):
        self.write({"state": "packed"})

    def action_mark_delivered(self):
        self.write({"state": "delivered"})

    def action_mark_missed(self):
        self.write({"state": "missed"})


class FarmCsaBoxLine(models.Model):
    _name = "farm.csa.box.line"
    _description = "CSA Box Line"
    _order = "box_id, sequence, id"

    box_id = fields.Many2one("farm.csa.box", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one("product.product", required=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    uom_id = fields.Many2one("uom.uom", related="product_id.uom_id", readonly=True)
    note = fields.Char()
