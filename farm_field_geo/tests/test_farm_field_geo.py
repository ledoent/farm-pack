from odoo.tests.common import TransactionCase


def _polygon_wkt(min_lon, min_lat, max_lon, max_lat):
    """Build a WGS84 rectangular polygon as WKT.

    Saves repeating the SRID prefix and the close-the-ring vertex across tests.
    """
    return (
        "SRID=4326;POLYGON(("
        f"{min_lon} {min_lat}, "
        f"{max_lon} {min_lat}, "
        f"{max_lon} {max_lat}, "
        f"{min_lon} {max_lat}, "
        f"{min_lon} {min_lat}"
        "))"
    )


# Reference polygon: ~0.01° square around Ligonier PA (40.242N, 79.245W).
# Albers reprojection of this rectangle is ~233 acres — the assertion ranges
# in the tests allow ±15% slack for projection edge cases.
LIGONIER_BIG = _polygon_wkt(-79.245, 40.242, -79.235, 40.252)
LIGONIER_SMALL = _polygon_wkt(-79.245, 40.242, -79.244, 40.243)


class TestFarmFieldGeo(TransactionCase):
    """Verify the polygon → acreage compute and its interaction with manual entry."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.farm = cls.env["res.partner"].create(
            {"name": "Test Farm", "is_company": True}
        )
        cls.crop = cls.env["farm.crop"].create({"name": "Corn"})

    def _make_field(self, geom=None, acres=None):
        vals = {
            "name": "North 40",
            "farm_partner_id": self.farm.id,
            "crop_id": self.crop.id,
        }
        if geom is not None:
            vals["geom"] = geom
        if acres is not None:
            vals["acres"] = acres
        return self.env["farm.field"].create(vals)

    def test_acres_manual_entry_persists_without_geom(self):
        # No polygon drawn yet — the user can set acres manually and the
        # compute must leave the manual value untouched. (The parent
        # `farm.field.acres` already defaults to 0.0, so to actually probe
        # the compute behaviour we set a distinctive value here.)
        field = self._make_field(acres=12.5)
        field.invalidate_recordset()
        self.assertEqual(field.acres, 12.5)

    def test_acres_compute_from_polygon(self):
        # ~0.01° square at 40N: one deg longitude is ~85 km here and one
        # deg latitude is ~111 km, so the rectangle is ~850 m × 1110 m ≈
        # 943,500 m² ≈ 233 acres. Allow generous slack for projection.
        field = self._make_field(geom=LIGONIER_BIG)
        self.assertGreater(field.acres, 200.0)
        self.assertLess(field.acres, 260.0)

    def test_acres_compute_overrides_manual_entry_on_geom_set(self):
        # User started with a manual estimate, then drew the boundary.
        # The compute should win.
        field = self._make_field(acres=999.0)
        self.assertEqual(field.acres, 999.0)
        field.geom = LIGONIER_BIG
        field.flush_recordset()
        field.invalidate_recordset()
        self.assertNotEqual(field.acres, 999.0)
        self.assertGreater(field.acres, 200.0)

    def test_acres_recomputes_on_geom_change(self):
        field = self._make_field(geom=LIGONIER_SMALL)
        small_acres = field.acres
        self.assertGreater(small_acres, 0.0)

        field.geom = LIGONIER_BIG
        field.flush_recordset()
        field.invalidate_recordset()
        self.assertGreater(
            field.acres, small_acres * 50, "Bigger polygon → bigger acreage"
        )

    def test_acres_deterministic_for_identical_polygon(self):
        # Two fields with the same boundary must report the same acreage.
        a = self._make_field(geom=LIGONIER_BIG)
        b = self._make_field(geom=LIGONIER_BIG)
        self.assertEqual(a.acres, b.acres)
