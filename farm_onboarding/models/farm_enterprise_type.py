from odoo import fields, models


class FarmEnterpriseType(models.Model):
    _name = "farm.enterprise.type"
    _description = "Farm Enterprise Type (eggs, vegetables, livestock, etc.)"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Char(translate=True)
    icon = fields.Char(help="Optional emoji or icon character for display.")
    is_animal = fields.Boolean()
    active = fields.Boolean(default=True)
