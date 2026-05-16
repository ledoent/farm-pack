from odoo import api, fields, models


class FarmMeasurementMixin(models.AbstractModel):
    """Mixin for any model carrying a value + unit pair.

    Concrete models inherit this to gain `measurement_value`, `measurement_uom_id`,
    and a computed display string. UoM category is left to the inheriting model
    (yield in mass, application rate in volume-per-area, etc.).
    """

    _name = "farm.measurement.mixin"
    _description = "Farm Measurement Mixin"

    measurement_value = fields.Float(string="Value", digits="Product Unit of Measure")
    measurement_uom_id = fields.Many2one("uom.uom", string="Unit")
    measurement_display = fields.Char(
        compute="_compute_measurement_display",
        store=False,
    )

    @api.depends("measurement_value", "measurement_uom_id")
    def _compute_measurement_display(self):
        for rec in self:
            if rec.measurement_uom_id:
                rec.measurement_display = (
                    f"{rec.measurement_value:g} {rec.measurement_uom_id.name}"
                )
            else:
                rec.measurement_display = f"{rec.measurement_value:g}"

    def measurement_to(self, target_uom):
        """Convert this record's measurement to `target_uom`. Returns a float."""
        self.ensure_one()
        if not self.measurement_uom_id or not target_uom:
            return self.measurement_value
        return self.measurement_uom_id._compute_quantity(
            self.measurement_value, target_uom
        )
