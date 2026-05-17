{
    "name": "Farm Harvest",
    "summary": "Harvest events: how much of which crop came off which field",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_planting",
        "farm_field",
        "farm_crop",
        "mail",
        "uom",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/farm_harvest_security.xml",
        "views/farm_harvest_views.xml",
        "views/farm_harvest_menu.xml",
    ],
    "demo": [
        "demo/farm_harvest_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
