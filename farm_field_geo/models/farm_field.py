from functools import lru_cache

from pyproj import Transformer
from shapely.ops import transform as shapely_transform

from odoo import api, fields, models

# Square meters in one US survey acre.
M2_PER_ACRE = 4046.8564224


@lru_cache(maxsize=1)
def _wgs84_to_albers_conus():
    """Build the EPSG:4326 → EPSG:5070 transformer once and reuse it.

    EPSG:5070 (Conus Albers Equal Area) is what NRCS and NASS use for
    lower-48 acreage. Reprojecting the WGS84 polygon there before measuring
    area gives a number that matches soil-survey + yield tooling for the
    same parcel.
    """
    return Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True).transform


class FarmField(models.Model):
    _inherit = "farm.field"

    geom = fields.GeoPolygon(
        string="Boundary",
        srid=4326,
        help="Field boundary as a WGS84 polygon. Drives the computed acreage; "
        "stored as PostGIS geometry.",
    )
    acres = fields.Float(
        compute="_compute_acres_from_geom",
        store=True,
        readonly=False,
        digits=(8, 2),
        help="Auto-computed from the polygon area when a boundary is drawn. "
        "Editable as a fallback for fields without a digitized boundary yet.",
    )

    @api.depends("geom")
    def _compute_acres_from_geom(self):
        # base_geoengine returns the field as a shapely geometry on read.
        # shapely has no `.transform()` method — reproject explicitly via
        # pyproj + shapely.ops.transform before measuring area.
        transformer = _wgs84_to_albers_conus()
        for rec in self:
            if not rec.geom:
                continue
            projected = shapely_transform(transformer, rec.geom)
            rec.acres = projected.area / M2_PER_ACRE
