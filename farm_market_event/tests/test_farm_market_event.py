from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFarmMarketEvent(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Event = cls.env["event.event"]
        cls.Offering = cls.env["farm.market.offering"]
        cls.SO = cls.env["sale.order"]
        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.Carrier = cls.env["delivery.carrier"]
        cls.delivery_product = cls.Product.create(
            {"name": "Shipping Service", "type": "service"}
        )

        cls.eggs = cls.Product.create(
            {"name": "Eggs Dozen", "type": "consu", "list_price": 6.0}
        )
        cls.tomatoes = cls.Product.create(
            {"name": "Tomatoes lb", "type": "consu", "list_price": 5.0}
        )
        cls.alice = cls.Partner.create({"name": "Alice"})
        cls.bob = cls.Partner.create({"name": "Bob"})

        cls.carrier = cls.Carrier.create(
            {
                "name": "Market Pickup",
                "delivery_type": "fixed",
                "product_id": cls.delivery_product.id,
                "is_farm_market_pickup": True,
            }
        )

        # An event a week from now, in the future, in preorder_open state
        future = datetime.now() + timedelta(days=7)
        cls.event = cls.Event.create(
            {
                "name": "Saturday Farmers Market",
                "date_begin": future,
                "date_end": future + timedelta(hours=4),
                "is_farm_market": True,
                "farm_market_state": "preorder_open",
                "farm_market_carrier_id": cls.carrier.id,
            }
        )
        cls.offer_eggs = cls.Offering.create(
            {
                "event_id": cls.event.id,
                "product_id": cls.eggs.id,
                "max_qty": 30,
                "list_price": 6.0,
            }
        )
        cls.offer_tomatoes = cls.Offering.create(
            {
                "event_id": cls.event.id,
                "product_id": cls.tomatoes.id,
                "max_qty": 20,
                "list_price": 5.0,
            }
        )

    def _create_preorder(self, partner, lines):
        so = self.SO.create(
            {
                "partner_id": partner.id,
                "carrier_id": self.carrier.id,
                "order_line": [
                    (0, 0, {"product_id": p.id, "product_uom_qty": q}) for p, q in lines
                ],
            }
        )
        return so

    def test_carrier_resolves_next_event(self):
        """The carrier should resolve to the next upcoming open event."""
        self.carrier.invalidate_recordset(["farm_market_next_event_id"])
        self.assertEqual(self.carrier.farm_market_next_event_id, self.event)

    def test_so_event_computed_from_carrier(self):
        so = self._create_preorder(self.alice, [(self.eggs, 2)])
        self.assertEqual(so.farm_market_event_id, self.event)

    def test_preorder_aggregates_per_product(self):
        self._create_preorder(self.alice, [(self.eggs, 2), (self.tomatoes, 3)])
        self._create_preorder(self.bob, [(self.eggs, 4)])
        self.offer_eggs.invalidate_recordset(["preorder_qty", "available_qty"])
        self.offer_tomatoes.invalidate_recordset(["preorder_qty", "available_qty"])
        self.assertEqual(self.offer_eggs.preorder_qty, 6.0)
        self.assertEqual(self.offer_tomatoes.preorder_qty, 3.0)
        self.assertEqual(self.offer_eggs.available_qty, 24.0)
        self.assertEqual(self.offer_tomatoes.available_qty, 17.0)

    def test_event_state_transitions(self):
        self.event.action_close_preorders()
        self.assertEqual(self.event.farm_market_state, "preorder_closed")
        self.event.action_go_live()
        self.assertEqual(self.event.farm_market_state, "live")
        self.event.action_close_market()
        self.assertEqual(self.event.farm_market_state, "closed")

    def test_preorder_after_cutoff_rejected(self):
        self.event.action_close_preorders()
        # After cutoff the carrier no longer resolves to this event, so SOs
        # would normally not get an event_id at all. To exercise the
        # cutoff guard, set the event back on the SO via the legacy direct
        # path: confirm a draft order while event is preorder_closed.
        self.event.action_open_preorders()
        so = self._create_preorder(self.alice, [(self.eggs, 1)])
        self.event.action_close_preorders()
        with self.assertRaises(ValidationError):
            # Force a write that triggers the constraint
            so.write({"note": "trigger constraint recheck"})

    def test_preorder_count_and_revenue(self):
        so = self._create_preorder(self.alice, [(self.eggs, 2), (self.tomatoes, 3)])
        so.action_confirm()
        self.event.invalidate_recordset(
            ["farm_preorder_count", "farm_preorder_revenue"]
        )
        self.assertEqual(self.event.farm_preorder_count, 1)
        # Confirmed SO total = 2*6 + 3*5 + delivery; delivery price = 0 for
        # the fixed-method test carrier, so revenue should be 27.0
        self.assertGreaterEqual(self.event.farm_preorder_revenue, 27.0)
