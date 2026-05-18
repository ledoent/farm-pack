from odoo.tests.common import TransactionCase

# Same reference rectangle farm_field_geo uses, but treated as a fence
# linestring tracing the perimeter. At 40N a 0.01° square is ~850 m ×
# 1110 m, so the full closed loop is ~3920 m ≈ 12,860 feet. The compute
# uses Albers reprojection, so we allow generous slack.
LIGONIER_PERIMETER_WKT = (
    "SRID=4326;LINESTRING("
    "-79.245 40.242, "
    "-79.235 40.242, "
    "-79.235 40.252, "
    "-79.245 40.252, "
    "-79.245 40.242"
    ")"
)


class TestFarmFence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.farm = cls.env["res.partner"].create(
            {"name": "Test Farm", "is_company": True}
        )
        cls.crop = cls.env["farm.crop"].create({"name": "Pasture", "code": "PAST"})
        cls.field = cls.env["farm.field"].create(
            {
                "name": "North 40",
                "farm_partner_id": cls.farm.id,
                "crop_id": cls.crop.id,
            }
        )

    def _make_fence(self, **overrides):
        vals = {
            "name": "Test Fence",
            "fence_type": "barbed_wire",
            "field_id": self.field.id,
        }
        vals.update(overrides)
        return self.env["farm.fence"].create(vals)

    def test_length_feet_zero_without_geom(self):
        # No line drawn yet → 0 feet, compute doesn't crash.
        fence = self._make_fence()
        self.assertEqual(fence.length_feet, 0.0)

    def test_length_feet_from_perimeter(self):
        # ~3.9 km perimeter → ~12,800 feet. Allow ±15% slack for projection.
        fence = self._make_fence(geom=LIGONIER_PERIMETER_WKT)
        self.assertGreater(fence.length_feet, 10000.0)
        self.assertLess(fence.length_feet, 15000.0)

    def test_length_recomputes_on_geom_change(self):
        fence = self._make_fence(
            geom="SRID=4326;LINESTRING(-79.245 40.242, -79.244 40.242)"
        )
        short = fence.length_feet
        self.assertGreater(short, 0.0)
        fence.geom = LIGONIER_PERIMETER_WKT
        fence.flush_recordset()
        fence.invalidate_recordset()
        self.assertGreater(fence.length_feet, short * 30)

    def test_condition_sort_priority_not_alphabetical(self):
        # Regression: an early version sorted by `condition desc` on the raw
        # selection key, which alpha-sorts "repair > good > fair" — fair
        # would hide below good. Verify the numeric rank sorts repairs first.
        good = self._make_fence(name="A — fence", condition="good")
        repair = self._make_fence(name="B — fence", condition="repair")
        fair = self._make_fence(name="C — fence", condition="fair")
        ordered = self.env["farm.fence"].search(
            [("id", "in", (good.id, fair.id, repair.id))]
        )
        self.assertEqual(
            ordered.mapped("condition"),
            ["repair", "fair", "good"],
            "Needs-repair must sort first; if you see good > fair > repair "
            "condition_rank lost its compute",
        )

    def test_condition_tracking(self):
        fence = self._make_fence(condition="good")
        initial = len(fence.message_ids)
        fence.condition = "repair"
        fence.flush_recordset()
        self.assertGreater(len(fence.message_ids), initial)

    def test_field_unlink_sets_field_id_null_not_cascade(self):
        # Perimeter fences span multiple fields — when one referenced field
        # is deleted, the fence should survive with field_id=None, not
        # cascade-delete. Verifies ondelete='set null'.
        temp_field = self.env["farm.field"].create(
            {
                "name": "Doomed",
                "farm_partner_id": self.farm.id,
                "crop_id": self.crop.id,
            }
        )
        fence = self._make_fence(field_id=temp_field.id)
        fence_id = fence.id
        temp_field.unlink()
        survivor = self.env["farm.fence"].browse(fence_id)
        survivor.invalidate_recordset()
        self.assertTrue(survivor.exists(), "Fence must survive its field's deletion")
        self.assertFalse(survivor.field_id, "field_id must be cleared, not retained")
