from odoo.tests.common import TransactionCase

from odoo.addons.farm_pack.hooks import post_init_hook


class TestPostInitHook(TransactionCase):
    """The hook only fires on the actual install transaction; here we
    re-invoke it inside a TransactionCase against the already-installed
    db and assert idempotency + the right set of users got a session.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Session = cls.env["farm.onboarding.session"]
        cls.farm_user_group = cls.env.ref("farm_base.group_farm_user")

    def test_hook_is_idempotent(self):
        # Re-running the install hook on a db that already went through
        # install must not duplicate sessions for existing users.
        before = self.Session.search_count([])
        post_init_hook(self.env)
        after = self.Session.search_count([])
        self.assertEqual(before, after)

    def test_hook_creates_session_for_new_farm_user(self):
        # Add a brand-new farm user that has no session yet, then re-run.
        new_user = self.env["res.users"].create(
            {
                "name": "Hook Test User",
                "login": "hook-test-user@example.com",
                "groups_id": [(4, self.farm_user_group.id)],
            }
        )
        self.assertEqual(
            self.Session.search_count([("user_id", "=", new_user.id)]),
            0,
            "fresh user must start with no sessions",
        )
        post_init_hook(self.env)
        self.assertGreater(
            self.Session.search_count([("user_id", "=", new_user.id)]),
            0,
            "hook must seed a session for a new farm user",
        )

    def test_hook_skips_portal_users(self):
        portal_group = self.env.ref("base.group_portal")
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal Test User",
                "login": "portal-test-user@example.com",
                "groups_id": [(6, 0, [portal_group.id])],
            }
        )
        post_init_hook(self.env)
        self.assertEqual(
            self.Session.search_count([("user_id", "=", portal_user.id)]),
            0,
            "portal users (share=True) must not get an onboarding session",
        )
