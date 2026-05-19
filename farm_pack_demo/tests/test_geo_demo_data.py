from odoo.tests.common import TransactionCase


class TestGeoDemoData(TransactionCase):
    """Smoke-check the geo demo fixtures load and produce sensible values.

    Catches XML parse errors, broken xmlid refs, and acreage-compute
    regressions on the demo polygons. The thresholds are wide because
    Albers reprojection over a small rectangle has noticeable edge
    effects — the test is here to detect "10x wrong" not "1% wrong".
    """

    def _ref(self, xmlid):
        return self.env.ref(f"farm_pack_demo.{xmlid}")

    def test_four_demo_fields_exist(self):
        fields = self.env["farm.field"].search(
            [
                (
                    "name",
                    "in",
                    ["North 40", "South Pasture", "East Garden", "Berry Hill"],
                )
            ]
        )
        self.assertEqual(len(fields), 4, "expected 4 named demo fields")

    def test_north_40_acreage_in_range(self):
        # Polygon at 40°N is roughly 0.004° × 0.004° → ~37 acres. Allow
        # a generous band: alarm only if we drop below 20 or above 60.
        field = self._ref("farm_field_demo_north_40")
        self.assertGreater(field.acres, 20)
        self.assertLess(field.acres, 60)

    def test_south_pasture_smaller_than_north_40(self):
        # The relative ordering is the most useful assertion — exact acreage
        # depends on projection details that vary by base_geoengine version.
        north = self._ref("farm_field_demo_north_40")
        south = self._ref("farm_field_demo_south_pasture")
        self.assertGreater(north.acres, south.acres)

    def test_east_garden_smallest_field(self):
        garden = self._ref("farm_field_demo_east_garden")
        # All other demo fields should be larger than the 2-ac veg plot.
        for other_xmlid in (
            "farm_field_demo_north_40",
            "farm_field_demo_south_pasture",
            "farm_field_demo_berry_hill",
        ):
            other = self._ref(other_xmlid)
            self.assertGreater(other.acres, garden.acres)

    def test_six_observations_loaded(self):
        # Each demo observation links to one of the four demo fields.
        demo_field_ids = (
            self.env["farm.field"]
            .search(
                [
                    (
                        "name",
                        "in",
                        ["North 40", "South Pasture", "East Garden", "Berry Hill"],
                    )
                ]
            )
            .ids
        )
        obs = self.env["farm.observation"].search([("field_id", "in", demo_field_ids)])
        self.assertEqual(len(obs), 6)
        # Cover the full urgency selection — each tier should appear.
        self.assertEqual(set(obs.mapped("urgency")), {"low", "med", "high"})

    def test_water_sources_serve_demo_fields(self):
        well = self._ref("farm_water_source_demo_house_well")
        self.assertEqual(well.source_type, "well")
        self.assertEqual(len(well.field_ids), 2)

    def test_three_fences_with_distinct_conditions(self):
        fences = [
            self._ref("farm_fence_demo_perimeter"),
            self._ref("farm_fence_demo_paddock_divider"),
            self._ref("farm_fence_demo_garden_enclosure"),
        ]
        conditions = {f.condition for f in fences}
        self.assertEqual(conditions, {"good", "fair", "repair"})
        # Length compute fires on every fence's GeoLine.
        for fence in fences:
            self.assertGreater(
                fence.length_feet, 0, f"{fence.name} should have positive length"
            )
