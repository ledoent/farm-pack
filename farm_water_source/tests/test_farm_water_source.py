from shapely.geometry import Point

from odoo.tests.common import TransactionCase


class TestFarmWaterSource(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.farm = cls.env["res.partner"].create(
            {"name": "Test Farm", "is_company": True}
        )
        cls.crop = cls.env["farm.crop"].create({"name": "Pasture"})
        cls.field_north = cls.env["farm.field"].create(
            {
                "name": "North 40",
                "farm_partner_id": cls.farm.id,
                "crop_id": cls.crop.id,
            }
        )
        cls.field_south = cls.env["farm.field"].create(
            {
                "name": "South Pasture",
                "farm_partner_id": cls.farm.id,
                "crop_id": cls.crop.id,
            }
        )

    def test_well_can_be_a_point(self):
        well = self.env["farm.water.source"].create(
            {
                "name": "House Well",
                "source_type": "well",
                "geom": Point(-79.245, 40.242),
            }
        )
        self.assertEqual(well.source_type, "well")
        self.assertTrue(well.geom)

    def test_pond_records_a_centroid_point(self):
        # v1 represents all source types as a single Point (well-head, tank
        # tap, pond centroid). Polygon footprint deferred to a follow-up.
        pond = self.env["farm.water.source"].create(
            {
                "name": "Big Pond",
                "source_type": "pond",
                "geom": Point(-79.2445, 40.2425),
            }
        )
        self.assertEqual(pond.source_type, "pond")
        self.assertTrue(pond.geom)

    def test_stream_records_an_access_point(self):
        # Streams record the access point where the user typically taps water
        # — full linestring for the stream itself is out of scope for v1.
        stream = self.env["farm.water.source"].create(
            {
                "name": "Burns Run access",
                "source_type": "stream",
                "geom": Point(-79.245, 40.242),
            }
        )
        self.assertEqual(stream.source_type, "stream")
        self.assertTrue(stream.geom)

    def test_fields_served_many2many(self):
        # Two fields drawing from one hydrant — the canonical use case for
        # field_ids: 'what fields does this source serve?'
        hydrant = self.env["farm.water.source"].create(
            {
                "name": "Pasture Hydrant",
                "source_type": "hydrant",
                "field_ids": [(6, 0, [self.field_north.id, self.field_south.id])],
            }
        )
        self.assertEqual(len(hydrant.field_ids), 2)
        self.assertIn(self.field_north, hydrant.field_ids)
        self.assertIn(self.field_south, hydrant.field_ids)
