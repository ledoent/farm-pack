"""Public storefront controllers for farmers market events.

Routes:
- /market — list of upcoming markets (preorder-open or planning)
- /market/<int:event_id> — single market detail with offerings + preorder form
- /market/<int:event_id>/preorder — POST: adds an offering's product to the
  customer's cart and sets carrier_id so farm_market_event_id auto-resolves
"""

from odoo import fields, http
from odoo.exceptions import ValidationError
from odoo.http import request


class WebsiteMarketController(http.Controller):
    @http.route(
        ["/market", "/market/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def market_list(self, page=1, **kw):
        now = fields.Datetime.now()
        events = (
            request.env["event.event"]
            .sudo()
            .search(
                [
                    ("is_farm_market", "=", True),
                    ("farm_market_state", "in", ("preorder_open", "planning")),
                    "|",
                    ("date_begin", "=", False),
                    ("date_begin", ">=", now),
                ],
                order="date_begin asc",
            )
        )
        return request.render(
            "farm_market_event_website.market_list_template",
            {"events": events},
        )

    @http.route(
        ["/market/<int:event_id>"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def market_detail(self, event_id, **kw):
        event = (
            request.env["event.event"]
            .sudo()
            .browse(event_id)
            .exists()
            .filtered(lambda e: e.is_farm_market)
        )
        if not event:
            raise request.not_found()
        return request.render(
            "farm_market_event_website.market_detail_template",
            {"event": event},
        )

    @http.route(
        ["/market/<int:event_id>/preorder"],
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def market_preorder(self, event_id, offering_id=None, quantity=1, **kw):
        event = (
            request.env["event.event"]
            .sudo()
            .browse(event_id)
            .exists()
            .filtered(lambda e: e.is_farm_market)
        )
        if not event:
            raise request.not_found()
        if event.farm_market_state != "preorder_open":
            return request.redirect(f"/market/{event_id}?error=preorders_closed")
        offering = request.env["farm.market.offering"].sudo().browse(int(offering_id))
        if not offering.exists() or offering.event_id != event:
            raise request.not_found()
        try:
            qty = max(1, int(quantity or 1))
        except (TypeError, ValueError):
            qty = 1
        order_sudo = request.website.sudo().sale_get_order(force_create=True)
        # Set the carrier so farm_market_event_id auto-resolves
        if event.farm_market_carrier_id and (
            not order_sudo.carrier_id
            or order_sudo.carrier_id != event.farm_market_carrier_id
        ):
            order_sudo.carrier_id = event.farm_market_carrier_id
        try:
            order_sudo._cart_update(
                product_id=offering.product_id.id,
                add_qty=qty,
            )
        except ValidationError:
            return request.redirect(f"/market/{event_id}?error=preorders_closed")
        return request.redirect("/shop/cart")
