{
    "name": "Farm Base",
    "summary": "Shared atoms for the farm pack: seasons, measurement and GPS mixins, ag units of measure",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "base",
        "uom",
        "mail",
    ],
    "data": [
        "security/farm_security.xml",
        "security/ir.model.access.csv",
        "data/farm_uom_data.xml",
        "views/farm_season_views.xml",
        "views/farm_menu.xml",
    ],
    "demo": [
        "demo/farm_season_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
