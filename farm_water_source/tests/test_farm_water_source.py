from odoo.tests.common import TransactionCase


class TestFarmWaterSource(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.farm = cls.env["res.partner"].create(
            {"name": "Test Farm", "is_company": True}
        )
        cls.crop = cls.env["farm.crop"].create({"name": "Pasture", "code": "PAST"})
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
        # Sanity check: a well is a point and the field saves.
        well = self.env["farm.water.source"].create(
            {
                "name": "House Well",
                "source_type": "well",
                "geom": "SRID=4326;POINT(-79.245 40.242)",
            }
        )
        self.assertEqual(well.source_type, "well")
        self.assertTrue(well.geom)

    def test_pond_can_be_a_polygon(self):
        # A pond is best represented as a polygon — GeoMultiGeometry must
        # accept that shape on the same column.
        pond = self.env["farm.water.source"].create(
            {
                "name": "Big Pond",
                "source_type": "pond",
                "geom": (
                    "SRID=4326;POLYGON(("
                    "-79.245 40.242, "
                    "-79.244 40.242, "
                    "-79.244 40.243, "
                    "-79.245 40.243, "
                    "-79.245 40.242"
                    "))"
                ),
            }
        )
        self.assertEqual(pond.source_type, "pond")
        self.assertTrue(pond.geom)

    def test_stream_can_be_a_linestring(self):
        # And a stream is best represented as a line — same column, third shape.
        stream = self.env["farm.water.source"].create(
            {
                "name": "Burns Run",
                "source_type": "stream",
                "geom": (
                    "SRID=4326;LINESTRING("
                    "-79.245 40.242, -79.240 40.245, -79.235 40.250"
                    ")"
                ),
            }
        )
        self.assertEqual(stream.source_type, "stream")
        self.assertTrue(stream.geom)

    def test_fields_served_many2many(self):
        # Two fields drawing from one well — the canonical use case for
        # field_ids: 'what fields does this source serve?'
        well = self.env["farm.water.source"].create(
            {
                "name": "Pasture Hydrant",
                "source_type": "hydrant",
                "field_ids": [(6, 0, [self.field_north.id, self.field_south.id])],
            }
        )
        self.assertEqual(len(well.field_ids), 2)
        self.assertIn(self.field_north, well.field_ids)
        self.assertIn(self.field_south, well.field_ids)
