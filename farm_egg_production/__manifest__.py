{
    "name": "Farm Egg Production",
    "summary": "Daily egg collection log per coop for homestead operators",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_base",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/farm_coop_views.xml",
        "views/farm_egg_collection_views.xml",
        "views/farm_egg_menu.xml",
    ],
    "demo": [
        "demo/farm_egg_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
