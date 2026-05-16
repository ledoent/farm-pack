{
    "name": "Farm Pack",
    "summary": "Umbrella: website + ordering + delivery + accounting for small farms",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        # ledoent — internal modules
        "farm_base",
        "farm_egg_production",
        "farm_csa",
        # farm_csa_contract_glue is held back: odoo-addon-contract has no
        # 19.0 wheel on the OCA wheelhouse yet (versions stop at 18.0.x).
        # Re-enable when OCA publishes the 19.0 release.
        "farm_delivery_routes",
        "farm_delivery_route_orders",
        "farm_market_event",
        "farm_market_event_website",
        "farm_onboarding",
        "farm_quickbooks_io",
        # Odoo CE — the four-jobs composition
        "website",
        "website_sale",
        "sale_management",
        "sale_stock",
        "stock_picking_batch",
        "delivery",
        "account",
        "event",
        "mass_mailing",
        "crm",
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "application": True,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
