from odoo import fields, models


class FarmMixin(models.AbstractModel):
    """Shared field bundle for farm models.

    Pulls in mail.thread + activity, a kanban color, an html notes field, and an
    active flag — the things 8+ farm models all want. Inherit alongside any model
    that needs them:

        class FarmField(models.Model):
            _name = "farm.field"
            _inherit = ["farm.mixin"]
            ...
    """

    _name = "farm.mixin"
    _description = "Farm Common Mixin"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    notes = fields.Html()
    color = fields.Integer(string="Kanban Color")
    active = fields.Boolean(default=True)
