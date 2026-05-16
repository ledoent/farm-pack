from collections import defaultdict

from odoo import api, fields, models


class FarmMarketPicklistWizard(models.TransientModel):
    _name = "farm.market.picklist.wizard"
    _description = "Pick List for a Farm Market"

    event_id = fields.Many2one("event.event", required=True)
    line_ids = fields.One2many("farm.market.picklist.wizard.line", "wizard_id")

    @api.model_create_multi
    def create(self, vals_list):
        wizards = super().create(vals_list)
        for wiz in wizards:
            wiz._populate_lines()
        return wizards

    def _populate_lines(self):
        self.ensure_one()
        if not self.event_id:
            return
        totals = defaultdict(float)
        preorders = self.event_id.farm_preorder_ids.filtered(
            lambda o: o.state in ("sale", "done", "draft", "sent")
        )
        for line in preorders.mapped("order_line"):
            totals[line.product_id.id] += line.product_uom_qty
        # Include offerings with no preorders yet so the farmer sees the
        # planned-max column.
        for offering in self.event_id.farm_offering_ids:
            if offering.product_id.id not in totals and offering.max_qty:
                totals[offering.product_id.id] = 0.0
        Line = self.env["farm.market.picklist.wizard.line"]
        for product_id, qty in totals.items():
            offering = self.event_id.farm_offering_ids.filtered(
                lambda o, pid=product_id: o.product_id.id == pid
            )[:1]
            Line.create(
                {
                    "wizard_id": self.id,
                    "product_id": product_id,
                    "preorder_qty": qty,
                    "max_qty": offering.max_qty if offering else 0.0,
                }
            )


class FarmMarketPicklistWizardLine(models.TransientModel):
    _name = "farm.market.picklist.wizard.line"
    _description = "Pick List Line (transient)"
    _order = "product_id"

    wizard_id = fields.Many2one(
        "farm.market.picklist.wizard", required=True, ondelete="cascade"
    )
    product_id = fields.Many2one("product.product", required=True)
    preorder_qty = fields.Float(string="Preorders")
    max_qty = fields.Float(string="Planned Max")
    recommended_qty = fields.Float(compute="_compute_recommended_qty")

    @api.depends("preorder_qty", "max_qty")
    def _compute_recommended_qty(self):
        """Recommend 1.5x preorder qty up to planned max — buffer for walk-up
        sales without over-stocking perishables."""
        for line in self:
            target = max(line.preorder_qty * 1.5, line.preorder_qty)
            if line.max_qty:
                target = min(target, line.max_qty)
            line.recommended_qty = target
