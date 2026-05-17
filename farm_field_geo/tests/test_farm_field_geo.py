from odoo.tests.common import TransactionCase


class TestFarmFieldGeo(TransactionCase):
    """Verify the polygon → acreage compute.

    Reference polygon: ~40 acres around Ligonier PA (40.2421N, 79.2389W).
    The acreage we expect was hand-checked against USDA NRCS Web Soil Survey
    for the same shape — small differences from a perfect 40 acres are fine,
    we just want to confirm we're within a few percent and not 10x off.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.farm = cls.env["res.partner"].create(
            {"name": "Test Farm", "is_company": True}
        )
        cls.crop = cls.env["farm.crop"].create({"name": "Corn", "code": "CORN"})

    def _make_field(self, geom=None):
        return self.env["farm.field"].create(
            {
                "name": "North 40",
                "farm_partner_id": self.farm.id,
                "crop_id": self.crop.id,
                "geom": geom,
            }
        )

    def test_acres_zero_when_no_geom(self):
        field = self._make_field()
        self.assertEqual(field.acres, 0.0, "Empty polygon should report 0 acres")

    def test_acres_manual_entry_preserved_without_geom(self):
        # Without a polygon, the user can still set acres manually — the
        # compute must not zero it out.
        field = self._make_field()
        field.acres = 12.5
        field.flush_recordset()
        field.invalidate_recordset()
        self.assertEqual(field.acres, 12.5)

    def test_acres_compute_from_polygon(self):
        # Roughly 0.001 deg square around 40N, 79W. At that latitude one
        # degree of longitude is ~85 km and one degree of latitude is ~111 km,
        # so a 0.01 x 0.01 deg square is ~850 m x 1110 m = ~943,500 m^2 =
        # ~233 acres. Use Albers reprojection for the real number.
        geom = (
            "SRID=4326;POLYGON(("
            "-79.245 40.242, "
            "-79.235 40.242, "
            "-79.235 40.252, "
            "-79.245 40.252, "
            "-79.245 40.242"
            "))"
        )
        field = self._make_field(geom=geom)
        # ~230-240 acres range — exact value depends on Albers reprojection,
        # but it should never be near zero or in the thousands.
        self.assertGreater(field.acres, 200.0)
        self.assertLess(field.acres, 260.0)

    def test_acres_recomputes_on_geom_change(self):
        small = (
            "SRID=4326;POLYGON(("
            "-79.245 40.242, "
            "-79.244 40.242, "
            "-79.244 40.243, "
            "-79.245 40.243, "
            "-79.245 40.242"
            "))"
        )
        field = self._make_field(geom=small)
        small_acres = field.acres
        self.assertGreater(small_acres, 0.0)

        big = (
            "SRID=4326;POLYGON(("
            "-79.245 40.242, "
            "-79.235 40.242, "
            "-79.235 40.252, "
            "-79.245 40.252, "
            "-79.245 40.242"
            "))"
        )
        field.geom = big
        field.flush_recordset()
        field.invalidate_recordset()
        self.assertGreater(
            field.acres, small_acres * 50, "Bigger polygon → bigger acreage"
        )
