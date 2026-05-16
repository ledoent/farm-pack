from odoo import fields, models
from odoo.exceptions import UserError

CADENCE_TO_RECURRING = {
    "weekly": ("weekly", 1),
    "biweekly": ("weekly", 2),
    "monthly": ("monthly", 1),
}


class FarmCsaSubscription(models.Model):
    _inherit = "farm.csa.subscription"

    contract_id = fields.Many2one(
        "contract.contract",
        string="Recurring Contract",
        readonly=True,
        copy=False,
        help="OCA contract that issues recurring invoices for this CSA "
        "subscription. Created on demand via 'Create Contract'.",
    )
    has_contract = fields.Boolean(compute="_compute_has_contract", store=True)

    def _compute_has_contract(self):
        for sub in self:
            sub.has_contract = bool(sub.contract_id)

    def action_create_contract(self):
        """Create an OCA contract.contract for recurring billing.

        Maps farm.csa.tier.cadence → OCA recurring_rule_type + interval:
        - weekly  → (weekly, 1)
        - biweekly → (weekly, 2)
        - monthly → (monthly, 1)

        Idempotent: returns the existing contract if already created.
        """
        Contract = self.env["contract.contract"]
        for sub in self:
            if sub.contract_id:
                continue
            if not sub.tier_id.product_id:
                raise UserError(
                    self.env._(
                        "CSA tier %(tier)s has no product configured; "
                        "cannot create a recurring contract.",
                        tier=sub.tier_id.name,
                    )
                )
            rule, interval = CADENCE_TO_RECURRING.get(
                sub.tier_id.cadence, ("monthly", 1)
            )
            line_vals = {
                "product_id": sub.tier_id.product_id.id,
                "name": sub.tier_id.product_id.name,
                "quantity": 1.0,
                "uom_id": sub.tier_id.product_id.uom_id.id,
                "price_unit": sub.tier_id.price_per_period,
                "recurring_rule_type": rule,
                "recurring_interval": interval,
                "recurring_invoicing_type": "post-paid",
                "date_start": sub.date_start or fields.Date.context_today(self),
            }
            if sub.date_end:
                line_vals["date_end"] = sub.date_end
            contract_vals = {
                "name": sub.name or f"CSA - {sub.partner_id.name}",
                "partner_id": sub.partner_id.id,
                "company_id": sub.company_id.id,
                "contract_type": "sale",
                "contract_line_ids": [(0, 0, line_vals)],
            }
            sub.contract_id = Contract.create(contract_vals)
        return True

    def action_open_contract(self):
        self.ensure_one()
        if not self.contract_id:
            raise UserError(self.env._("No contract attached yet."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "contract.contract",
            "res_id": self.contract_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_activate(self):
        """Auto-create the contract when the subscription is activated."""
        res = super().action_activate()
        for sub in self.filtered(lambda s: not s.contract_id):
            sub.action_create_contract()
        return res

    def action_cancel(self):
        """Mark the linked contract as canceled too."""
        res = super().action_cancel()
        for sub in self.filtered(lambda s: s.contract_id):
            # OCA contract's terminate action requires a date + reason;
            # MVP just sets date_end to today on all contract lines.
            today = fields.Date.context_today(self)
            sub.contract_id.contract_line_ids.write({"date_end": today})
        return res
