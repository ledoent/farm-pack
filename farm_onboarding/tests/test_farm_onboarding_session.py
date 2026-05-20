from odoo.tests.common import TransactionCase


class TestFarmOnboardingSession(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Session = cls.env["farm.onboarding.session"]
        cls.EnterpriseType = cls.env["farm.enterprise.type"]

    def test_default_state_is_welcome(self):
        sess = self.Session.create({})
        self.assertEqual(sess.state, "welcome")
        self.assertFalse(sess.finished_at)

    def test_advance_through_all_states(self):
        sess = self.Session.create({})
        sess.action_next()
        self.assertEqual(sess.state, "farm_profile")
        sess.action_next()
        self.assertEqual(sess.state, "enterprises")
        sess.action_next()
        self.assertEqual(sess.state, "books")
        sess.action_next()
        self.assertEqual(sess.state, "done")
        self.assertTrue(sess.finished_at)

    def test_back_button(self):
        sess = self.Session.create({"state": "books"})
        sess.action_back()
        self.assertEqual(sess.state, "enterprises")
        sess.action_back()
        self.assertEqual(sess.state, "farm_profile")
        sess.action_back()
        self.assertEqual(sess.state, "welcome")
        # Back from welcome stays at welcome
        sess.action_back()
        self.assertEqual(sess.state, "welcome")

    def test_skip_jumps_to_done(self):
        sess = self.Session.create({"state": "enterprises"})
        sess.action_skip()
        self.assertEqual(sess.state, "done")
        self.assertTrue(sess.finished_at)

    def test_restart_clears_finished_at(self):
        sess = self.Session.create({"state": "done"})
        sess.action_restart()
        self.assertEqual(sess.state, "welcome")
        self.assertFalse(sess.finished_at)

    def test_progress_pct_at_each_state(self):
        states_to_pct = {
            "welcome": 0,
            "farm_profile": 25,
            "enterprises": 50,
            "books": 75,
            "done": 100,
        }
        for state, expected in states_to_pct.items():
            sess = self.Session.create({"state": state})
            self.assertEqual(sess.progress_pct, expected)

    def test_get_or_create_returns_existing_open_session(self):
        first = self.Session.get_or_create_for_current_user()
        self.assertTrue(first)
        second = self.Session.get_or_create_for_current_user()
        self.assertEqual(first.id, second.id)

    def test_get_or_create_creates_new_after_done(self):
        first = self.Session.get_or_create_for_current_user()
        first.action_skip()
        second = self.Session.get_or_create_for_current_user()
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(second.state, "welcome")

    def test_enterprise_data_loaded(self):
        eggs = self.env.ref("farm_onboarding.enterprise_eggs", raise_if_not_found=False)
        self.assertTrue(eggs)
        self.assertTrue(eggs.is_animal)

    def test_enterprise_selection_persists(self):
        eggs = self.env.ref("farm_onboarding.enterprise_eggs")
        veggies = self.env.ref("farm_onboarding.enterprise_vegetables")
        sess = self.Session.create({"enterprise_ids": [(6, 0, [eggs.id, veggies.id])]})
        self.assertEqual(len(sess.enterprise_ids), 2)

    def test_count_pending_for_current_user(self):
        # Drives the systray bell — must return 0 when nothing pending,
        # > 0 when an active session exists. Don't count `done` sessions.
        # Start from a clean slate: archive any sessions that exist for
        # the test user from prior tests in this case.
        self.Session.search([("user_id", "=", self.env.user.id)]).write(
            {"state": "done", "finished_at": "2026-01-01"}
        )
        self.assertEqual(self.Session.count_pending_for_current_user(), 0)

        self.Session.get_or_create_for_current_user()
        self.assertEqual(self.Session.count_pending_for_current_user(), 1)

        # Skipping completes the session — bell should go away.
        self.Session.get_or_create_for_current_user().action_skip()
        self.assertEqual(self.Session.count_pending_for_current_user(), 0)
