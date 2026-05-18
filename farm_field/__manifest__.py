{
    "name": "Farm Field",
    "summary": "Fields / plots where crops grow — name, acres, current crop, organic",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_base",
        "farm_crop",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/farm_field_security.xml",
        "views/farm_field_views.xml",
        "views/farm_field_menu.xml",
    ],
    "demo": [
        "demo/farm_field_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
