from odoo import api, fields, models


class FarmObservation(models.Model):
    _name = "farm.observation"
    _description = "Field Observation"
    _inherit = ["mail.thread", "farm.rank.mixin"]
    # High-urgency, recent items rise to the top of every list / kanban.
    # `rank` comes from farm.rank.mixin (mirrors `urgency` through the
    # selection→int map below so DESC sort gives high→med→low instead of
    # alpha-DESC's med→low→high).
    _order = "rank desc, observation_date desc"
    # Enforces field_id.company_id == observation.company_id at write time.
    _check_company_auto = True
    # farm.rank.mixin wiring:
    _rank_selection_field = "urgency"
    _rank_value_map = {"low": 0, "med": 1, "high": 2}

    field_id = fields.Many2one(
        "farm.field",
        string="Field",
        required=True,
        index=True,
        ondelete="cascade",
        check_company=True,
        help="Which field this observation was captured on.",
    )
    name = fields.Char(
        compute="_compute_name",
        store=True,
        help="Auto-generated label combining the field, type, and date.",
    )
    observation_type = fields.Selection(
        [
            ("pest", "Pest Damage"),
            ("disease", "Disease"),
            ("weed", "Weed Pressure"),
            ("soil", "Soil Condition"),
            ("water", "Water / Drainage"),
            ("yield", "Yield Issue"),
            ("photo", "Photo Survey"),
            ("other", "Other"),
        ],
        required=True,
        default="photo",
        tracking=True,
    )
    geom = fields.GeoPoint(
        string="Location",
        srid=4326,
        help="Point where this observation was made. Set by clicking on the map "
        "in the form view, or auto-populated from photo EXIF GPS tags in a "
        "future release.",
    )
    observation_date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )
    notes = fields.Text(required=True)
    photo_id = fields.Many2one(
        "ir.attachment",
        string="Photo",
        domain="[('mimetype', 'ilike', 'image/')]",
        help="Attach a single representative photo. Use chatter attachments "
        "for multiple shots.",
    )
    urgency = fields.Selection(
        [
            ("low", "Low"),
            ("med", "Medium"),
            ("high", "High"),
        ],
        default="low",
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        related="field_id.company_id",
        store=True,
        index=True,
    )

    @api.depends("field_id", "observation_type", "observation_date")
    def _compute_name(self):
        # E.g. "North 40 — Pest Damage — 2026-05-17"
        type_labels = dict(self._fields["observation_type"].selection)
        for rec in self:
            field_name = rec.field_id.name or "?"
            type_label = type_labels.get(rec.observation_type, "?")
            date_str = (
                rec.observation_date and rec.observation_date.date().isoformat() or "?"
            )
            rec.name = f"{field_name} — {type_label} — {date_str}"
