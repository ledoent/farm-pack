from odoo.tests.common import TransactionCase


class TestFarmHarvest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.field = cls.env["farm.field"].create({"name": "H-1"})
        cls.tomato = cls.env.ref("farm_crop.crop_tomato")
        cls.uom_lb = cls.env.ref("uom.product_uom_lb")
        cls.planting = cls.env["farm.planting"].create(
            {
                "field_id": cls.field.id,
                "crop_id": cls.tomato.id,
                "plant_date": "2026-04-01",
            }
        )

    def test_from_planting_inherits_field_crop(self):
        h = self.env["farm.harvest"].create(
            {
                "planting_id": self.planting.id,
                "harvest_date": "2026-07-15",
                "qty_harvested": 30.0,
                "qty_uom_id": self.uom_lb.id,
            }
        )
        self.assertEqual(h.field_id, self.field)
        self.assertEqual(h.crop_id, self.tomato)

    def test_standalone_record(self):
        h = self.env["farm.harvest"].create(
            {
                "field_id": self.field.id,
                "crop_id": self.tomato.id,
                "harvest_date": "2026-08-01",
                "qty_harvested": 12.5,
                "qty_uom_id": self.uom_lb.id,
            }
        )
        self.assertFalse(h.planting_id)
        self.assertEqual(h.qty_harvested, 12.5)

    def test_name_auto_composed(self):
        h = self.env["farm.harvest"].create(
            {
                "field_id": self.field.id,
                "crop_id": self.tomato.id,
                "harvest_date": "2026-08-01",
                "qty_harvested": 7,
                "qty_uom_id": self.uom_lb.id,
            }
        )
        self.assertIn("7", h.name)
        self.assertIn("Tomato", h.name)
        self.assertIn("2026-08-01", h.name)

    def test_clearing_planting_keeps_field_crop(self):
        """Documented behavior: clearing planting_id does NOT reset field/crop
        — the compute only fires when planting_id is set. Codified so a future
        refactor doesn't silently break it."""
        h = self.env["farm.harvest"].create(
            {
                "planting_id": self.planting.id,
                "harvest_date": "2026-07-15",
                "qty_harvested": 30.0,
                "qty_uom_id": self.uom_lb.id,
            }
        )
        original_field = h.field_id
        h.planting_id = False
        self.assertEqual(h.field_id, original_field)
