{
    "name": "Farm Delivery Routes",
    "summary": "Drop-off points and weekly delivery routes for homestead operators",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/farm_dropoff_point_views.xml",
        "views/farm_delivery_route_views.xml",
        "views/farm_delivery_menu.xml",
    ],
    "demo": [
        "demo/farm_delivery_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
