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

    def test_hook_skips_user_holding_both_portal_and_farm_groups(self):
        # Defensive: the share=False filter is what excludes portal users.
        # A user with both base.group_portal AND farm_base.group_farm_user
        # has share=True (set by the portal-group implication), so they
        # must still be excluded — otherwise we'd surface the wizard to
        # an account that can't actually use it.
        portal_group = self.env.ref("base.group_portal")
        hybrid = self.env["res.users"].create(
            {
                "name": "Hybrid Portal+Farm User",
                "login": "hybrid-user@example.com",
                "groups_id": [(6, 0, [portal_group.id, self.farm_user_group.id])],
            }
        )
        self.assertTrue(hybrid.share, "portal-implied share flag must be set")
        post_init_hook(self.env)
        self.assertEqual(
            self.Session.search_count([("user_id", "=", hybrid.id)]),
            0,
            "share=True users must be excluded regardless of farm-group membership",
        )

    def test_hook_seeds_one_session_per_company_for_multi_company_user(self):
        # The hook iterates user.company_ids — a user with access to two
        # companies should get two sessions (each company is its own
        # onboarding scope). Future refactors that switch to env.company
        # would silently regress this; the test pins the behavior.
        second_company = self.env["res.company"].create({"name": "Multi-Co Test Farm"})
        multi_co_user = self.env["res.users"].create(
            {
                "name": "Multi-Co Farm User",
                "login": "multi-co-user@example.com",
                "groups_id": [(4, self.farm_user_group.id)],
                "company_ids": [
                    (4, self.env.company.id),
                    (4, second_company.id),
                ],
                "company_id": self.env.company.id,
            }
        )
        post_init_hook(self.env)
        sessions = self.Session.search([("user_id", "=", multi_co_user.id)])
        self.assertEqual(
            len(sessions),
            2,
            "multi-company farm user must get one session per company",
        )
        self.assertEqual(
            sorted(sessions.mapped("company_id").ids),
            sorted([self.env.company.id, second_company.id]),
            "the two sessions must target the two companies in company_ids",
        )
