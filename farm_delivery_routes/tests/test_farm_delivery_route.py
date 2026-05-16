from odoo.tests.common import TransactionCase


class TestFarmDeliveryRoute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Point = cls.env["farm.dropoff.point"]
        cls.Route = cls.env["farm.delivery.route"]
        cls.p1 = cls.Point.create({"name": "Porch 1", "kind": "home"})
        cls.p2 = cls.Point.create({"name": "Pantry", "kind": "pantry"})

    def test_route_lifecycle_completes_pending_stops(self):
        route = self.Route.create(
            {
                "name": "Test Route",
                "scheduled_date": "2030-04-15",
                "stop_ids": [
                    (0, 0, {"dropoff_point_id": self.p1.id, "package_count": 2}),
                    (0, 0, {"dropoff_point_id": self.p2.id, "package_count": 5}),
                ],
            }
        )
        self.assertEqual(route.state, "planned")
        self.assertEqual(route.stop_count, 2)
        route.action_start()
        self.assertEqual(route.state, "in_progress")
        route.stop_ids[0].action_mark_delivered()
        route.action_complete()
        self.assertEqual(route.state, "completed")
        self.assertEqual(route.stop_ids.mapped("state"), ["delivered", "delivered"])

    def test_skipped_stops_stay_skipped(self):
        route = self.Route.create(
            {
                "name": "Skip Test",
                "scheduled_date": "2030-04-16",
                "stop_ids": [
                    (0, 0, {"dropoff_point_id": self.p1.id}),
                    (0, 0, {"dropoff_point_id": self.p2.id}),
                ],
            }
        )
        route.stop_ids[1].action_mark_skipped()
        route.action_start()
        route.action_complete()
        self.assertEqual(route.stop_ids[0].state, "delivered")
        self.assertEqual(route.stop_ids[1].state, "skipped")
