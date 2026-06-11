from odoo.tests.common import TransactionCase


class TestFarmObservation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.farm = cls.env["res.partner"].create(
            {"name": "Test Farm", "is_company": True}
        )
        cls.crop = cls.env["farm.crop"].create({"name": "Corn"})
        cls.field = cls.env["farm.field"].create(
            {
                "name": "North 40",
                "farm_partner_id": cls.farm.id,
                "crop_id": cls.crop.id,
            }
        )

    def _make_obs(self, **overrides):
        vals = {
            "field_id": self.field.id,
            "observation_type": "pest",
            "notes": "Aphids on the south edge",
        }
        vals.update(overrides)
        return self.env["farm.observation"].create(vals)

    def test_name_includes_field_type_and_date(self):
        # Name should auto-compose from field + type + date so users see
        # something meaningful in lists without opening the form.
        obs = self._make_obs(observation_type="pest")
        self.assertIn(self.field.name, obs.name)
        self.assertIn("Pest", obs.name)
        self.assertIn(str(obs.observation_date.year), obs.name)

    def test_name_recomputes_on_field_change(self):
        obs = self._make_obs()
        original_name = obs.name
        other_field = self.env["farm.field"].create(
            {
                "name": "South Pasture",
                "farm_partner_id": self.farm.id,
                "crop_id": self.crop.id,
            }
        )
        obs.field_id = other_field
        obs.flush_recordset()
        obs.invalidate_recordset()
        self.assertNotEqual(obs.name, original_name)
        self.assertIn("South Pasture", obs.name)

    def test_urgency_tracking_declared_on_field(self):
        # The urgency field should declare tracking=True so mail.thread
        # writes audit chatter on changes. Probe the field definition
        # rather than mail.thread's plumbing — testing Odoo's tracking
        # delivery is the framework's job, not ours.
        field = self.env["farm.observation"]._fields["urgency"]
        self.assertTrue(field.tracking, "urgency field must declare tracking=True")

    def test_company_id_inherits_from_field(self):
        obs = self._make_obs()
        self.assertEqual(obs.company_id, self.field.company_id)

    def test_geom_optional(self):
        # Observations made far from the farmhouse may have no GPS yet —
        # geom is optional, the record still saves.
        obs = self._make_obs(geom=None)
        self.assertFalse(obs.geom)

    def test_urgency_sort_priority_not_alphabetical(self):
        # Regression: an early version sorted by `urgency desc` on the raw
        # selection key, which alpha-sorts "med" above "high". Verify the
        # numeric rank actually puts high-urgency first.
        low = self._make_obs(urgency="low", notes="cosmetic")
        high = self._make_obs(urgency="high", notes="actively dying")
        med = self._make_obs(urgency="med", notes="watch this")
        ordered = self.env["farm.observation"].search(
            [("id", "in", (low.id, med.id, high.id))]
        )
        self.assertEqual(
            ordered.mapped("urgency"),
            ["high", "med", "low"],
            "high urgency must sort first; "
            "if you see ['med', 'low', 'high'], farm.rank.mixin's rank "
            "compute isn't wired to urgency anymore",
        )
