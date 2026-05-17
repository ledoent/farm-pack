from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, new_test_user


class TestFarmField(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tomato = cls.env.ref("farm_crop.crop_tomato")

    def test_create_minimal(self):
        field = self.env["farm.field"].create({"name": "Test Field 1"})
        self.assertEqual(field.name, "Test Field 1")
        self.assertTrue(field.active)
        self.assertEqual(field.acres, 0.0)
        self.assertEqual(field.company_id, self.env.company)

    def test_create_with_crop(self):
        field = self.env["farm.field"].create(
            {"name": "Tomato Patch", "crop_id": self.tomato.id, "acres": 0.5}
        )
        self.assertEqual(field.crop_id, self.tomato)
        self.assertEqual(field.acres, 0.5)

    def test_organic_toggle(self):
        field = self.env["farm.field"].create({"name": "Cert Field"})
        self.assertFalse(field.organic_certified)
        field.organic_certified = True
        self.assertTrue(field.organic_certified)

    def test_multi_company_isolation(self):
        """A user in company A can't see fields in company B (ir.rule)."""
        company_a = self.env["res.company"].create({"name": "Farm Co A"})
        company_b = self.env["res.company"].create({"name": "Farm Co B"})
        user_a = new_test_user(
            self.env,
            login="farm_user_a",
            groups="farm_base.group_farm_user",
            company_id=company_a.id,
            company_ids=[(6, 0, [company_a.id])],
        )
        field_b = self.env["farm.field"].create(
            {"name": "B's Field", "company_id": company_b.id}
        )
        # User A in company A can't read company B's field.
        with self.assertRaises(AccessError):
            field_b.with_user(user_a).read(["name"])
