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
    # All source types record a single point: the well-head, the tank tap,
    # the centroid of the pond, the access point on the stream. We picked
    # this in v1 because base_geoengine 19.0 (PR #446 head) doesn't ship a
    # GeoAnyGeometry type — a future farm_water_source_polygon module can
    # add an optional polygon footprint for ponds / streams when a customer
    # asks for surface-area calculations.
    geom = fields.GeoPoint(string="Location", srid=4326)
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
