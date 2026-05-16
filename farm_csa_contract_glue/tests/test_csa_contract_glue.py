from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestCsaContractGlue(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.Partner = cls.env["res.partner"]
        cls.Tier = cls.env["farm.csa.tier"]
        cls.Subscription = cls.env["farm.csa.subscription"]
        cls.product = cls.Product.create(
            {"name": "CSA Family Weekly", "type": "service", "list_price": 42.0}
        )
        cls.partner = cls.Partner.create({"name": "Test Member"})
        cls.tier_weekly = cls.Tier.create(
            {
                "name": "Family Weekly",
                "product_id": cls.product.id,
                "cadence": "weekly",
                "price_per_period": 42.0,
            }
        )
        cls.tier_biweekly = cls.Tier.create(
            {
                "name": "Small Biweekly",
                "product_id": cls.product.id,
                "cadence": "biweekly",
                "price_per_period": 25.0,
            }
        )
        cls.tier_monthly = cls.Tier.create(
            {
                "name": "Monthly Special",
                "product_id": cls.product.id,
                "cadence": "monthly",
                "price_per_period": 100.0,
            }
        )

    def _create_sub(self, tier):
        return self.Subscription.create(
            {
                "partner_id": self.partner.id,
                "tier_id": tier.id,
                "date_start": "2030-01-01",
            }
        )

    def test_weekly_subscription_creates_weekly_contract(self):
        sub = self._create_sub(self.tier_weekly)
        sub.action_create_contract()
        self.assertTrue(sub.contract_id)
        self.assertTrue(sub.has_contract)
        line = sub.contract_id.contract_line_ids[:1]
        self.assertEqual(line.recurring_rule_type, "weekly")
        self.assertEqual(line.recurring_interval, 1)
        self.assertEqual(line.price_unit, 42.0)

    def test_biweekly_maps_to_weekly_interval_2(self):
        sub = self._create_sub(self.tier_biweekly)
        sub.action_create_contract()
        line = sub.contract_id.contract_line_ids[:1]
        self.assertEqual(line.recurring_rule_type, "weekly")
        self.assertEqual(line.recurring_interval, 2)

    def test_monthly_maps_to_monthly_rule(self):
        sub = self._create_sub(self.tier_monthly)
        sub.action_create_contract()
        line = sub.contract_id.contract_line_ids[:1]
        self.assertEqual(line.recurring_rule_type, "monthly")
        self.assertEqual(line.recurring_interval, 1)

    def test_create_contract_is_idempotent(self):
        sub = self._create_sub(self.tier_weekly)
        sub.action_create_contract()
        first = sub.contract_id
        sub.action_create_contract()
        self.assertEqual(sub.contract_id, first)

    def test_activate_auto_creates_contract(self):
        sub = self._create_sub(self.tier_weekly)
        sub.action_activate()
        self.assertEqual(sub.state, "active")
        self.assertTrue(sub.contract_id)

    def test_cancel_ends_contract_lines(self):
        sub = self._create_sub(self.tier_weekly)
        sub.action_activate()
        sub.action_cancel()
        for line in sub.contract_id.contract_line_ids:
            self.assertTrue(line.date_end)

    def test_open_contract_action(self):
        sub = self._create_sub(self.tier_weekly)
        sub.action_create_contract()
        action = sub.action_open_contract()
        self.assertEqual(action["res_id"], sub.contract_id.id)
        self.assertEqual(action["res_model"], "contract.contract")

    def test_open_contract_errors_without_contract(self):
        sub = self._create_sub(self.tier_weekly)
        with self.assertRaises(UserError):
            sub.action_open_contract()
