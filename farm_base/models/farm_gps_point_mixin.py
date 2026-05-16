from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FarmGpsPointMixin(models.AbstractModel):
    """Mixin giving any model an optional WGS84 lat/lon pair.

    Used by farm.field (centroid), farm.spray.log (application point),
    farm.livestock.animal (last-known location), etc.
    """

    _name = "farm.gps.point.mixin"
    _description = "Farm GPS Point Mixin"

    gps_latitude = fields.Float(string="Latitude", digits=(10, 7))
    gps_longitude = fields.Float(string="Longitude", digits=(10, 7))
    gps_display = fields.Char(compute="_compute_gps_display", store=False)

    @api.depends("gps_latitude", "gps_longitude")
    def _compute_gps_display(self):
        for rec in self:
            if rec.gps_latitude or rec.gps_longitude:
                rec.gps_display = f"{rec.gps_latitude:.6f}, {rec.gps_longitude:.6f}"
            else:
                rec.gps_display = False

    @api.constrains("gps_latitude", "gps_longitude")
    def _check_gps_bounds(self):
        for rec in self:
            if rec.gps_latitude and not -90.0 <= rec.gps_latitude <= 90.0:
                raise ValidationError(self.env._("Latitude must be between -90 and 90."))
            if rec.gps_longitude and not -180.0 <= rec.gps_longitude <= 180.0:
                raise ValidationError(
                    self.env._("Longitude must be between -180 and 180.")
                )
