from datetime import datetime, timedelta

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteMarket(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Carrier = cls.env["delivery.carrier"]
        Event = cls.env["event.event"]
        Offering = cls.env["farm.market.offering"]
        Product = cls.env["product.product"]

        cls.delivery_product = Product.create(
            {"name": "Shipping Service", "type": "service"}
        )
        cls.carrier = Carrier.create(
            {
                "name": "Market Pickup",
                "delivery_type": "fixed",
                "product_id": cls.delivery_product.id,
                "is_farm_market_pickup": True,
            }
        )
        future = datetime.now() + timedelta(days=7)
        cls.event = Event.create(
            {
                "name": "Saturday Farmers Market",
                "date_begin": future,
                "date_end": future + timedelta(hours=4),
                "is_farm_market": True,
                "farm_market_state": "preorder_open",
                "farm_market_carrier_id": cls.carrier.id,
            }
        )
        cls.eggs = Product.create(
            {
                "name": "Eggs Dozen",
                "type": "consu",
                "list_price": 6.0,
                "sale_ok": True,
                "is_published": True,
            }
        )
        cls.offering = Offering.create(
            {
                "event_id": cls.event.id,
                "product_id": cls.eggs.id,
                "max_qty": 30,
                "list_price": 6.0,
            }
        )

    def test_market_list_page_loads(self):
        resp = self.url_open("/market")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Saturday Farmers Market", resp.text)

    def test_market_detail_page_shows_offering(self):
        resp = self.url_open(f"/market/{self.event.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Eggs Dozen", resp.text)
        self.assertIn("Preorder", resp.text)

    def test_market_detail_unknown_returns_404(self):
        # mute_logger because raise request.not_found() logs an info-level
        # warning that the checklog hook treats as a CI failure otherwise.
        from odoo.tools import mute_logger

        with mute_logger("odoo.http"):
            resp = self.url_open("/market/999999")
        self.assertEqual(resp.status_code, 404)
