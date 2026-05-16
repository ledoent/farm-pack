from odoo import fields, models


class FarmQboImportWizard(models.TransientModel):
    _name = "farm.qbo.import.wizard"
    _description = "Start a QuickBooks Import"

    connection_id = fields.Many2one("farm.qbo.connection", required=True)
    lookback_months = fields.Selection(
        [
            ("3", "Last 3 months"),
            ("12", "Last 12 months"),
            ("36", "Last 36 months"),
            ("all", "All history"),
        ],
        default="12",
        required=True,
    )
    include_coa = fields.Boolean(string="Chart of Accounts", default=True)
    include_partners = fields.Boolean(string="Vendors + Customers", default=True)
    include_products = fields.Boolean(string="Items / Products", default=True)
    include_transactions = fields.Boolean(string="Transactions", default=False)

    def action_start(self):
        self.ensure_one()
        import_rec = self.env["farm.qbo.import"].create(
            {
                "connection_id": self.connection_id.id,
                "lookback_months": self.lookback_months,
                "include_coa": self.include_coa,
                "include_partners": self.include_partners,
                "include_products": self.include_products,
                "include_transactions": self.include_transactions,
            }
        )
        import_rec.action_run_pull()
        return {
            "type": "ir.actions.act_window",
            "res_model": "farm.qbo.import",
            "res_id": import_rec.id,
            "view_mode": "form",
            "target": "current",
        }
