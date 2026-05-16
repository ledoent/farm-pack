from psycopg2.errors import CheckViolation, UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


class TestFarmSeason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Season = cls.env["farm.season"]

    def test_create_and_state_transitions(self):
        s = self.Season.create(
            {
                "name": "Test Season 2030",
                "date_start": "2030-03-01",
                "date_end": "2030-08-31",
            }
        )
        self.assertEqual(s.state, "planning")
        s.action_activate()
        self.assertEqual(s.state, "active")
        s.action_close()
        self.assertEqual(s.state, "closed")

    def test_end_before_start_rejected(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(CheckViolation):
            with self.env.cr.savepoint():
                self.Season.create(
                    {
                        "name": "Backwards 2030",
                        "date_start": "2030-08-31",
                        "date_end": "2030-03-01",
                    }
                )

    def test_overlapping_seasons_rejected(self):
        self.Season.create(
            {
                "name": "Spring 2030",
                "date_start": "2030-03-01",
                "date_end": "2030-08-31",
            }
        )
        with self.assertRaises(ValidationError):
            self.Season.create(
                {
                    "name": "Summer 2030",
                    "date_start": "2030-06-01",
                    "date_end": "2030-09-30",
                }
            )

    def test_name_unique_per_company(self):
        self.Season.create(
            {
                "name": "Duplicate Season",
                "date_start": "2031-03-01",
                "date_end": "2031-08-31",
            }
        )
        with mute_logger("odoo.sql_db"), self.assertRaises(UniqueViolation):
            with self.env.cr.savepoint():
                self.Season.create(
                    {
                        "name": "Duplicate Season",
                        "date_start": "2032-03-01",
                        "date_end": "2032-08-31",
                    }
                )
