{
    "name": "Farm Planting",
    "summary": "Planting events: which crop went into which field and when",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_field",
        "farm_crop",
        "mail",
        "uom",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/farm_planting_security.xml",
        "views/farm_planting_views.xml",
        "views/farm_planting_menu.xml",
    ],
    "demo": [
        "demo/farm_planting_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
