from odoo.tests.common import TransactionCase


class TestFarmQbo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Connection = cls.env["farm.qbo.connection"]
        cls.Import = cls.env["farm.qbo.import"]
        cls.connection = cls.Connection.create(
            {"environment": "sandbox", "realm_id": "test_realm"}
        )

    def test_connection_state_disconnected_without_tokens(self):
        self.assertEqual(self.connection.state, "disconnected")

    def test_connection_state_connected_with_tokens(self):
        from datetime import timedelta

        from odoo import fields

        self.connection.write(
            {
                "access_token": "fake",
                "refresh_token": "refresh",
                "token_expires_at": fields.Datetime.now() + timedelta(hours=1),
            }
        )
        self.connection.invalidate_recordset(["state"])
        self.assertEqual(self.connection.state, "connected")

    def test_import_pull_with_stub_creates_mappings(self):
        imp = self.Import.create({"connection_id": self.connection.id})
        imp.action_run_pull()
        self.assertEqual(imp.state, "review")
        self.assertGreater(imp.mapping_count, 0)
        types = set(imp.mapping_ids.mapped("qbo_type"))
        self.assertIn("account", types)
        self.assertIn("partner", types)
        self.assertIn("product", types)

    def test_import_commit_creates_account_records(self):
        imp = self.Import.create(
            {
                "connection_id": self.connection.id,
                "include_partners": False,
                "include_products": False,
            }
        )
        imp.action_run_pull()
        account_count_before = self.env["account.account"].search_count([])
        imp.action_commit()
        self.assertEqual(imp.state, "committed")
        account_count_after = self.env["account.account"].search_count([])
        self.assertGreater(account_count_after, account_count_before)
        committed_mappings = imp.mapping_ids.filtered("committed_target_ref")
        self.assertGreater(len(committed_mappings), 0)

    def test_import_rollback_reverses_commit(self):
        imp = self.Import.create(
            {
                "connection_id": self.connection.id,
                "include_partners": False,
                "include_products": False,
            }
        )
        imp.action_run_pull()
        imp.action_commit()
        # Verify commit added accounts referenced by mappings
        for m in imp.mapping_ids:
            self.assertTrue(m.committed_target_ref)
        imp.action_rollback()
        self.assertEqual(imp.state, "rolled_back")
        for m in imp.mapping_ids:
            self.assertFalse(m.committed_target_ref)

    def test_wizard_creates_and_starts_import(self):
        Wizard = self.env["farm.qbo.import.wizard"]
        wiz = Wizard.create(
            {
                "connection_id": self.connection.id,
                "lookback_months": "3",
                "include_partners": False,
                "include_products": False,
                "include_transactions": False,
            }
        )
        action = wiz.action_start()
        imp = self.Import.browse(action["res_id"])
        self.assertEqual(imp.state, "review")
        self.assertEqual(imp.lookback_months, "3")
