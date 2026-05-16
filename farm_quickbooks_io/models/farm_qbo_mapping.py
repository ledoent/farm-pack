import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FarmQboMapping(models.Model):
    _name = "farm.qbo.mapping"
    _description = "QBO Entity Mapping Proposal"
    _order = "import_id, qbo_type, confidence desc"

    import_id = fields.Many2one(
        "farm.qbo.import", required=True, ondelete="cascade", index=True
    )
    qbo_type = fields.Selection(
        [
            ("account", "Chart of Accounts Entry"),
            ("partner", "Vendor / Customer"),
            ("product", "Item / Product"),
            ("fixed_asset", "Fixed Asset"),
            ("transaction", "Transaction"),
        ],
        required=True,
        index=True,
    )
    qbo_external_id = fields.Char(required=True, index=True)
    qbo_label = fields.Char(help="Display name from QBO for human review.")
    qbo_payload = fields.Text(help="Raw JSON payload from the QBO API.")

    proposed_target_model = fields.Char(
        help="Odoo model this maps to, e.g. account.account, res.partner.",
    )
    proposed_target_ref = fields.Char(
        help="XML id or 'model,id' tuple for the proposed Odoo target record.",
    )
    proposed_schedule_f_line = fields.Char(
        help="Mapped Schedule F line (for account mappings only).",
    )
    confidence = fields.Float(default=0.0, group_operator="avg")
    source = fields.Selection(
        [
            ("rule", "Rule Layer"),
            ("ai", "AI Layer"),
            ("user", "User"),
        ],
        default="rule",
        required=True,
    )
    rationale = fields.Text(help="One-sentence explanation, surfaced on hover.")

    user_decision = fields.Selection(
        [
            ("accept", "Accept"),
            ("edit", "Edit"),
            ("reject", "Reject"),
        ],
        help="Operator's decision. Empty means 'go with the proposal'.",
    )
    committed_target_ref = fields.Char(
        readonly=True,
        help="Odoo reference once committed, used for rollback.",
    )

    def _commit(self):
        """Create or link the Odoo record for this mapping.

        MVP only implements the account branch via the dictionary lookup;
        partners and products are stubbed and left for follow-up. Each
        committed mapping writes its committed_target_ref so rollback works.
        """
        for rec in self:
            if rec.qbo_type == "account":
                rec._commit_account()
            elif rec.qbo_type == "partner":
                rec._commit_partner()
            elif rec.qbo_type == "product":
                rec._commit_product()

    def _commit_account(self):
        self.ensure_one()
        payload = json.loads(self.qbo_payload or "{}")
        code = (payload.get("AcctNum") or f"QBO{self.qbo_external_id}")[:64]
        name = payload.get("Name") or self.qbo_label or self.qbo_external_id
        Account = self.env["account.account"]
        existing = Account.search(
            [
                ("code", "=", code),
                ("company_ids", "in", self.import_id.company_id.id),
            ],
            limit=1,
        )
        if existing:
            account = existing
        else:
            account = Account.create(
                {
                    "code": code,
                    "name": name,
                    "account_type": self._guess_account_type(payload),
                    "company_ids": [(4, self.import_id.company_id.id)],
                }
            )
        self.committed_target_ref = f"account.account,{account.id}"

    def _guess_account_type(self, payload):
        classification = (payload.get("Classification") or "").lower()
        sub = (payload.get("AccountSubType") or "").lower()
        if classification == "revenue":
            return "income"
        if classification == "expense":
            return "expense"
        if classification == "asset":
            if "current" in sub or "bank" in sub:
                return "asset_current"
            return "asset_non_current"
        if classification == "liability":
            if "current" in sub:
                return "liability_current"
            return "liability_non_current"
        if classification == "equity":
            return "equity"
        return "asset_current"

    def _commit_partner(self):
        self.ensure_one()
        payload = json.loads(self.qbo_payload or "{}")
        Partner = self.env["res.partner"]
        partner = Partner.create(
            {
                "name": payload.get("DisplayName") or self.qbo_label,
                "email": (payload.get("PrimaryEmailAddr") or {}).get("Address"),
            }
        )
        self.committed_target_ref = f"res.partner,{partner.id}"

    def _commit_product(self):
        self.ensure_one()
        payload = json.loads(self.qbo_payload or "{}")
        Product = self.env["product.product"]
        product = Product.create(
            {
                "name": payload.get("Name") or self.qbo_label,
                "list_price": payload.get("UnitPrice") or 0.0,
                "type": "consu",
            }
        )
        self.committed_target_ref = f"product.product,{product.id}"

    def _rollback(self):
        """Delete the committed Odoo record (best-effort).

        Failure to delete (FK constraints from downstream usage) leaves the
        record in place and notes the failure on audit_log; we don't unwind
        partial rollbacks.
        """
        for rec in self:
            if not rec.committed_target_ref:
                continue
            try:
                model, rid = rec.committed_target_ref.split(",")
                target = self.env[model].browse(int(rid))
                if target.exists():
                    target.unlink()
                rec.committed_target_ref = False
            except Exception as e:  # noqa: BLE001
                _logger.warning("QBO rollback for mapping %s failed: %s", rec.id, e)

    @api.constrains("import_id", "qbo_type", "qbo_external_id")
    def _check_uniqueness(self):
        for rec in self:
            duplicate = self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("import_id", "=", rec.import_id.id),
                    ("qbo_type", "=", rec.qbo_type),
                    ("qbo_external_id", "=", rec.qbo_external_id),
                ]
            )
            if duplicate:
                raise models.ValidationError(
                    self.env._(
                        "Duplicate mapping for QBO %(qbo_type)s id=%(qbo_id)s "
                        "in this import.",
                        qbo_type=rec.qbo_type,
                        qbo_id=rec.qbo_external_id,
                    )
                )
