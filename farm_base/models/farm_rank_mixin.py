from odoo import api, fields, models


class FarmRankMixin(models.AbstractModel):
    """Selection-with-priority-rank helper for sortable models.

    Several farm-pack models declare a Selection field whose **string
    keys** don't sort alphabetically the way human-priority does. The
    canonical example is observation urgency: `low / med / high` —
    alpha-DESC gives "med > low > high" (m > l > h), which means
    high-urgency items hide below medium ones in any list ordered by
    that column.

    The pattern this mixin extracts:

    1. Subclass declares the user-visible Selection field as normal
       (any name, any keys, any labels).
    2. Subclass sets two class attributes pointing the mixin at that
       field:

        class FarmObservation(models.Model):
            _inherit = ["mail.thread", "farm.rank.mixin"]
            _order = "rank desc, observation_date desc"
            _rank_selection_field = "urgency"
            _rank_value_map = {"low": 0, "med": 1, "high": 2}

            urgency = fields.Selection([
                ("low", "Low"), ("med", "Medium"), ("high", "High"),
            ], required=True, default="low")

    3. The mixin contributes a stored, indexed `rank` Integer that
       mirrors the selection key through `_rank_value_map`. The
       subclass picks `rank` up in `_order` to get a real
       priority sort.

    Why not just rename selection keys? Two reasons:
    - Keys are persisted to the DB and surface in xmlrpc / search
      domains; "low/med/high" reads better than "0/1/2".
    - Renaming requires a migration script; this mixin adds a column
      without changing the existing column.
    """

    _name = "farm.rank.mixin"
    _description = "Selection-with-priority-rank helper"

    # Subclasses MUST override these two attributes.
    _rank_selection_field = ""
    _rank_value_map: dict[str, int] = {}

    rank = fields.Integer(
        compute="_compute_rank",
        store=True,
        index=True,
        readonly=True,
        help="Numeric mirror of the configured selection field. Subclasses "
        "should use `rank desc` in `_order` to get a priority sort that "
        "actually matches the conceptual ordering of the selection keys.",
    )

    def _rank_depends(self):
        """Override hook — return the field names the rank depends on.

        Defaults to the configured selection field. Override if a
        subclass derives rank from multiple fields.
        """
        return [self._rank_selection_field] if self._rank_selection_field else []

    @api.depends(lambda self: self._rank_depends())
    def _compute_rank(self):
        sel_field = self._rank_selection_field
        rank_map = self._rank_value_map
        if not sel_field or not rank_map:
            for rec in self:
                rec.rank = 0
            return
        for rec in self:
            rec.rank = rank_map.get(rec[sel_field], 0)
