{
    "name": "Farm CSA",
    "summary": "CSA shares, weekly box composition, member subscriptions",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_base",
        "product",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/farm_csa_tier_views.xml",
        "views/farm_csa_subscription_views.xml",
        "views/farm_csa_box_views.xml",
        "views/farm_csa_menu.xml",
    ],
    "demo": [
        "demo/farm_csa_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
