from odoo.tests.common import TransactionCase


class TestFarmCsa(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tier = cls.env["farm.csa.tier"]
        cls.Subscription = cls.env["farm.csa.subscription"]
        cls.Box = cls.env["farm.csa.box"]
        cls.product = cls.env["product.product"].create(
            {"name": "Test Share", "type": "service", "list_price": 30.0}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Member"})
        cls.tier = cls.Tier.create(
            {
                "name": "Test Weekly",
                "product_id": cls.product.id,
                "cadence": "weekly",
                "price_per_period": 30.0,
            }
        )

    def test_subscription_lifecycle(self):
        sub = self.Subscription.create(
            {
                "partner_id": self.partner.id,
                "tier_id": self.tier.id,
                "date_start": "2030-01-01",
            }
        )
        self.assertEqual(sub.state, "draft")
        sub.action_activate()
        self.assertEqual(sub.state, "active")
        sub.action_pause()
        self.assertEqual(sub.state, "paused")
        sub.action_cancel()
        self.assertEqual(sub.state, "cancelled")

    def test_box_lifecycle_and_lines(self):
        sub = self.Subscription.create(
            {
                "partner_id": self.partner.id,
                "tier_id": self.tier.id,
                "date_start": "2030-01-01",
                "state": "active",
            }
        )
        produce = self.env["product.product"].create(
            {"name": "Test Carrots", "type": "consu"}
        )
        box = self.Box.create(
            {
                "subscription_id": sub.id,
                "delivery_date": "2030-01-08",
                "line_ids": [
                    (0, 0, {"product_id": produce.id, "quantity": 2}),
                ],
            }
        )
        self.assertEqual(box.partner_id, self.partner)
        self.assertEqual(box.line_count, 1)
        box.action_mark_packed()
        self.assertEqual(box.state, "packed")
        box.action_mark_delivered()
        self.assertEqual(box.state, "delivered")

    def test_tier_subscription_count(self):
        for _i in range(3):
            partner = self.env["res.partner"].create({"name": "Member"})
            self.Subscription.create(
                {
                    "partner_id": partner.id,
                    "tier_id": self.tier.id,
                    "date_start": "2030-01-01",
                    "state": "active",
                }
            )
        self.tier.invalidate_recordset(["subscription_count"])
        self.assertEqual(self.tier.subscription_count, 3)
