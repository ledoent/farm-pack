from odoo import fields, models


class FarmWaterSource(models.Model):
    _name = "farm.water.source"
    _description = "Water Source"
    _order = "name"

    name = fields.Char(required=True)
    source_type = fields.Selection(
        [
            ("well", "Well"),
            ("tank", "Surface Tank"),
            ("pond", "Pond"),
            ("stream", "Stream / Creek"),
            ("trough", "Trough"),
            ("spring", "Spring"),
            ("hydrant", "Hydrant / Spigot"),
        ],
        required=True,
    )
    # GeoMultiGeometry holds Point, LineString, or Polygon — the right shape
    # depends on the source type (well/trough/spring/hydrant = point,
    # stream = linestring, pond/tank = polygon). One column keeps the model
    # simple at the cost of looser validation; an admin who really wants the
    # constraint can layer it on later.
    geom = fields.GeoMultiGeometry(string="Location", srid=4326)
    field_ids = fields.Many2many(
        "farm.field",
        string="Fields Served",
        help="Which fields draw from this source. Drives the 'where is this "
        "field's water coming from' query.",
    )
    capacity_gallons = fields.Float(
        digits=(10, 0),
        help="Practical usable volume in gallons. Leave blank for streams / "
        "springs where flow rate matters more than reservoir capacity.",
    )
    last_tested_date = fields.Date(help="Most recent potability / coliform test.")
    quality_notes = fields.Text()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
