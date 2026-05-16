from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestWeeklyRouteWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Zone = cls.env["farm.delivery.zone"]
        cls.Wizard = cls.env["farm.weekly.route.wizard"]
        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.SO = cls.env["sale.order"]

        cls.zone_north = cls.Zone.create({"name": "North", "code": "N", "sequence": 1})
        cls.zone_south = cls.Zone.create({"name": "South", "code": "S", "sequence": 2})
        cls.customer_n = cls.Partner.create({"name": "North Customer"})
        cls.customer_s = cls.Partner.create({"name": "South Customer"})
        cls.product = cls.Product.create(
            {"name": "Eggs Dozen", "type": "consu", "list_price": 6.0}
        )

    def _create_confirmed_order(self, partner, zone, delivery_date):
        so = self.SO.create(
            {
                "partner_id": partner.id,
                "farm_delivery_date": delivery_date,
                "farm_delivery_zone_id": zone.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 6.0,
                        },
                    )
                ],
            }
        )
        so.action_confirm()
        return so

    def test_wizard_errors_when_no_matching_pickings(self):
        wiz = self.Wizard.create(
            {
                "delivery_date": "2030-01-01",
                "delivery_zone_id": self.zone_north.id,
            }
        )
        with self.assertRaises(UserError):
            wiz.action_build_route()

    def test_wizard_groups_pickings_by_date_and_zone(self):
        self._create_confirmed_order(self.customer_n, self.zone_north, "2030-01-05")
        so_s = self._create_confirmed_order(
            self.customer_s, self.zone_south, "2030-01-05"
        )
        wiz = self.Wizard.create(
            {
                "delivery_date": "2030-01-05",
                "delivery_zone_id": self.zone_north.id,
            }
        )
        action = wiz.action_build_route()
        batch = self.env["stock.picking.batch"].browse(action["res_id"])
        # Batch should only include north-zone picking
        picking_partners = batch.picking_ids.mapped("partner_id")
        self.assertIn(self.customer_n, picking_partners)
        self.assertNotIn(self.customer_s, picking_partners)
        # Batch carries denormalized date + zone
        self.assertEqual(str(batch.farm_delivery_date), "2030-01-05")
        self.assertEqual(batch.farm_delivery_zone_id, self.zone_north)
        # South order untouched
        self.assertFalse(so_s.picking_ids.batch_id)

    def test_wizard_without_zone_pulls_all_zones(self):
        self._create_confirmed_order(self.customer_n, self.zone_north, "2030-01-06")
        self._create_confirmed_order(self.customer_s, self.zone_south, "2030-01-06")
        wiz = self.Wizard.create({"delivery_date": "2030-01-06"})
        action = wiz.action_build_route()
        batch = self.env["stock.picking.batch"].browse(action["res_id"])
        self.assertEqual(len(batch.picking_ids), 2)
