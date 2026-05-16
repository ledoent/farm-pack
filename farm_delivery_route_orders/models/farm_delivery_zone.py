from odoo import fields, models


class FarmDeliveryZone(models.Model):
    _name = "farm.delivery.zone"
    _description = "Farm Delivery Zone"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(help="Short code for printouts, e.g. 'N' or 'MKT'.")
    sequence = fields.Integer(default=10)
    color = fields.Integer(default=0)
    description = fields.Text()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        index=True,
    )
