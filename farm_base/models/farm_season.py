from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FarmSeason(models.Model):
    _name = "farm.season"
    _description = "Farm Season"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, name"
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short code used in reports and exports, e.g. 'S26' for Spring 2026.",
    )
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        [
            ("planning", "Planning"),
            ("active", "Active"),
            ("closed", "Closed"),
        ],
        default="planning",
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    note = fields.Html()

    _season_dates_order = models.Constraint(
        "CHECK (date_end >= date_start)",
        "A season's end date must be on or after its start date.",
    )
    _season_name_company_unique = models.Constraint(
        "UNIQUE (name, company_id)",
        "A season name must be unique within a company.",
    )

    @api.constrains("date_start", "date_end", "company_id")
    def _check_no_overlap(self):
        for season in self:
            overlap = self.search(
                [
                    ("id", "!=", season.id),
                    ("company_id", "=", season.company_id.id),
                    ("date_start", "<=", season.date_end),
                    ("date_end", ">=", season.date_start),
                ],
                limit=1,
            )
            if overlap:
                raise ValidationError(
                    self.env._(
                        "Season %(this)s overlaps with %(other)s.",
                        this=season.display_name,
                        other=overlap.display_name,
                    )
                )

    def action_activate(self):
        self.write({"state": "active"})

    def action_close(self):
        self.write({"state": "closed"})
