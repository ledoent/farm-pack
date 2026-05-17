from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFarmPlanting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.field = cls.env["farm.field"].create({"name": "T-1"})
        cls.tomato = cls.env.ref("farm_crop.crop_tomato")  # 75 days to maturity

    def test_create_planting(self):
        p = self.env["farm.planting"].create(
            {
                "field_id": self.field.id,
                "crop_id": self.tomato.id,
                "plant_date": "2026-04-01",
            }
        )
        self.assertEqual(p.state, "planted")
        self.assertIn("Tomato", p.name)
        self.assertIn("T-1", p.name)

    def test_name_precomputed_on_create(self):
        """`name` is required by no field but computed-stored-precompute, so
        external reads right after create see a value."""
        p = self.env["farm.planting"].create(
            {
                "field_id": self.field.id,
                "crop_id": self.tomato.id,
                "plant_date": "2026-04-01",
            }
        )
        # Use read() to bypass any in-memory cache.
        self.assertTrue(p.read(["name"])[0]["name"])

    def test_expected_harvest_auto_computed(self):
        p = self.env["farm.planting"].create(
            {
                "field_id": self.field.id,
                "crop_id": self.tomato.id,
                "plant_date": "2026-04-01",
            }
        )
        self.assertEqual(p.expected_harvest_date, date(2026, 6, 15))

    def test_expected_harvest_override(self):
        p = self.env["farm.planting"].create(
            {
                "field_id": self.field.id,
                "crop_id": self.tomato.id,
                "plant_date": "2026-04-01",
                "expected_harvest_date": "2026-08-01",
            }
        )
        self.assertEqual(p.expected_harvest_date, date(2026, 8, 1))

    def test_harvest_before_plant_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["farm.planting"].create(
                {
                    "field_id": self.field.id,
                    "crop_id": self.tomato.id,
                    "plant_date": "2026-04-01",
                    "expected_harvest_date": "2026-03-01",
                }
            )

    def test_state_transitions(self):
        p = self.env["farm.planting"].create(
            {"field_id": self.field.id, "crop_id": self.tomato.id}
        )
        self.assertEqual(p.state, "planted")
        p.action_mark_growing()
        self.assertEqual(p.state, "growing")
        p.action_mark_harvested()
        self.assertEqual(p.state, "harvested")

    def test_company_from_field(self):
        """planting.company_id is populated from field.company_id at INSERT time
        (precompute=True), so ir.rule binds correctly."""
        p = self.env["farm.planting"].create(
            {"field_id": self.field.id, "crop_id": self.tomato.id}
        )
        self.assertEqual(
            p.read(["company_id"])[0]["company_id"][0], self.field.company_id.id
        )
