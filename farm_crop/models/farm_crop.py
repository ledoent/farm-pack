from odoo import fields, models


class FarmCrop(models.Model):
    _name = "farm.crop"
    _description = "Farm Crop"
    # image.mixin ships the standard image_128/256/512/1024/1920 fields with
    # properly labeled strings (Image, Small Image, etc.). Inheriting it
    # avoids the duplicate-label warning the OCA checklog catches when each
    # size is declared manually with no string= override.
    _inherit = ["farm.mixin", "image.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    latin_name = fields.Char(
        string="Scientific Name",
        help="Latin binomial, e.g. 'Solanum lycopersicum' for tomato.",
    )
    category = fields.Selection(
        [
            ("vegetable", "Vegetable"),
            ("fruit", "Fruit"),
            ("grain", "Grain"),
            ("legume", "Legume"),
            ("herb", "Herb"),
            ("cover", "Cover Crop"),
            ("forage", "Forage"),
            ("flower", "Cut Flower"),
            ("other", "Other"),
        ],
        default="vegetable",
        required=True,
        tracking=True,
    )
    family = fields.Char(
        string="Botanical Family",
        help="e.g. 'Solanaceae' (nightshades), 'Brassicaceae' (brassicas) — "
        "useful for crop rotation planning.",
    )
    days_to_maturity = fields.Integer(
        help="Typical days from planting to first harvest under your conditions.",
    )
    # image_1920 + image_128 come from image.mixin (see _inherit above).
