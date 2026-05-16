import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FarmQboImport(models.Model):
    _name = "farm.qbo.import"
    _description = "QuickBooks Online Import Session"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"
    _check_company_auto = True

    name = fields.Char(compute="_compute_name", store=True)
    connection_id = fields.Many2one(
        "farm.qbo.connection", required=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pulling", "Pulling Data"),
            ("mapping", "Mapping"),
            ("review", "Awaiting Review"),
            ("committing", "Committing"),
            ("committed", "Committed"),
            ("rolled_back", "Rolled Back"),
            ("failed", "Failed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
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
    raw_payload_attachment_id = fields.Many2one(
        "ir.attachment",
        readonly=True,
        help="Raw QBO API responses archived for replay + audit.",
    )
    audit_log = fields.Text(readonly=True)
    error_message = fields.Text(readonly=True)
    mapping_ids = fields.One2many("farm.qbo.mapping", "import_id")
    mapping_count = fields.Integer(compute="_compute_mapping_count")
    pulled_at = fields.Datetime(readonly=True)
    committed_at = fields.Datetime(readonly=True)

    @api.depends("connection_id", "create_date")
    def _compute_name(self):
        for rec in self:
            if rec.connection_id and rec.create_date:
                rec.name = (
                    f"{rec.connection_id.environment} · "
                    f"{rec.create_date.date().isoformat()}"
                )
            else:
                rec.name = self.env._("Draft Import")

    @api.depends("mapping_ids")
    def _compute_mapping_count(self):
        for rec in self:
            rec.mapping_count = len(rec.mapping_ids)

    def action_run_pull(self):
        """Pull entities from QBO and create mapping proposals.

        MVP implementation uses the QboPuller service which falls back to a
        deterministic stub fixture when the intuit-oauth/python-quickbooks
        libraries are not installed — so the UI is testable without real
        Intuit credentials.
        """
        from ..services.qbo_puller import QboPuller

        for rec in self:
            if rec.state not in ("draft", "failed"):
                raise UserError(
                    self.env._(
                        "Cannot start a pull when import is in state %s.",
                        rec.state,
                    )
                )
            rec.write({"state": "pulling", "error_message": False})
            try:
                puller = QboPuller(rec)
                result = puller.pull()
                rec.write(
                    {
                        "state": "mapping",
                        "pulled_at": fields.Datetime.now(),
                        "audit_log": json.dumps(result.get("summary", {})),
                    }
                )
                rec._build_mapping_proposals(result)
                rec.state = "review"
            except Exception as e:  # noqa: BLE001
                _logger.exception("QBO pull failed for import %s", rec.id)
                rec.write({"state": "failed", "error_message": str(e)})
                raise UserError(self.env._("QBO pull failed: %s", e)) from e

    def _build_mapping_proposals(self, pull_result):
        """Turn raw QBO entities into farm.qbo.mapping rows.

        Uses the rule-layer dictionary (data/qbo_account_dictionary.xml) for
        Schedule F line classification. AI layer can override later via the
        farm.ai.provider interface (ledoent_farm_ai module).
        """
        Mapping = self.env["farm.qbo.mapping"]
        rows = []
        for account in pull_result.get("accounts", []):
            rows.append(
                {
                    "import_id": self.id,
                    "qbo_type": "account",
                    "qbo_external_id": account.get("Id"),
                    "qbo_payload": json.dumps(account),
                    "qbo_label": account.get("Name")
                    or account.get("FullyQualifiedName"),
                    "confidence": 0.8,
                    "source": "rule",
                }
            )
        for partner in pull_result.get("partners", []):
            rows.append(
                {
                    "import_id": self.id,
                    "qbo_type": "partner",
                    "qbo_external_id": partner.get("Id"),
                    "qbo_payload": json.dumps(partner),
                    "qbo_label": partner.get("DisplayName"),
                    "confidence": 0.9,
                    "source": "rule",
                }
            )
        for product in pull_result.get("products", []):
            rows.append(
                {
                    "import_id": self.id,
                    "qbo_type": "product",
                    "qbo_external_id": product.get("Id"),
                    "qbo_payload": json.dumps(product),
                    "qbo_label": product.get("Name"),
                    "confidence": 0.85,
                    "source": "rule",
                }
            )
        if rows:
            Mapping.create(rows)

    def action_commit(self):
        """Materialise accepted mappings into real Odoo records."""
        for rec in self:
            if rec.state != "review":
                raise UserError(
                    self.env._(
                        "Only imports in 'Awaiting Review' state can be committed."
                    )
                )
            rec.write({"state": "committing"})
            try:
                accepted = rec.mapping_ids.filtered(
                    lambda m: m.user_decision in ("accept", False)
                    and not m.committed_target_ref
                )
                for mapping in accepted:
                    mapping._commit()
                rec.write(
                    {
                        "state": "committed",
                        "committed_at": fields.Datetime.now(),
                    }
                )
            except Exception as e:  # noqa: BLE001
                _logger.exception("QBO commit failed for import %s", rec.id)
                rec.write({"state": "failed", "error_message": str(e)})
                raise UserError(self.env._("Commit failed: %s", e)) from e

    def action_rollback(self):
        for rec in self:
            if rec.state != "committed":
                raise UserError(
                    self.env._("Only committed imports can be rolled back.")
                )
            for mapping in rec.mapping_ids.filtered("committed_target_ref"):
                mapping._rollback()
            rec.state = "rolled_back"

    def action_reset_to_draft(self):
        self.mapping_ids.unlink()
        self.write({"state": "draft", "error_message": False})
