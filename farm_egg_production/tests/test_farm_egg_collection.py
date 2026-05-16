from psycopg2.errors import UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


class TestFarmEggCollection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Coop = cls.env["farm.coop"]
        cls.Collection = cls.env["farm.egg.collection"]
        cls.coop = cls.Coop.create({"name": "Test Coop", "active_bird_count": 6})

    def test_available_count_computed(self):
        rec = self.Collection.create(
            {
                "coop_id": self.coop.id,
                "collection_date": "2030-04-15",
                "count_total": 10,
                "count_broken": 1,
                "count_kept_home": 3,
            }
        )
        self.assertEqual(rec.count_available, 6)

    def test_available_never_negative(self):
        rec = self.Collection.create(
            {
                "coop_id": self.coop.id,
                "collection_date": "2030-04-16",
                "count_total": 3,
                "count_broken": 2,
                "count_kept_home": 2,
            }
        )
        self.assertEqual(rec.count_available, 0)

    def test_one_per_coop_per_day(self):
        self.Collection.create(
            {
                "coop_id": self.coop.id,
                "collection_date": "2030-04-17",
                "count_total": 5,
            }
        )
        with mute_logger("odoo.sql_db"), self.assertRaises(UniqueViolation):
            with self.env.cr.savepoint():
                self.Collection.create(
                    {
                        "coop_id": self.coop.id,
                        "collection_date": "2030-04-17",
                        "count_total": 8,
                    }
                )

    def test_subcounts_cannot_exceed_total(self):
        with self.assertRaises(ValidationError):
            self.Collection.create(
                {
                    "coop_id": self.coop.id,
                    "collection_date": "2030-04-18",
                    "count_total": 5,
                    "count_broken": 4,
                    "count_kept_home": 2,
                }
            )

    def test_coop_eggs_last_7_days(self):
        from datetime import timedelta

        from odoo import fields

        today = fields.Date.context_today(self.env.user)
        for offset, count in enumerate([8, 9, 11]):
            self.Collection.create(
                {
                    "coop_id": self.coop.id,
                    "collection_date": today - timedelta(days=offset),
                    "count_total": count,
                }
            )
        self.coop.invalidate_recordset(["eggs_last_7_days"])
        self.assertEqual(self.coop.eggs_last_7_days, 28)
