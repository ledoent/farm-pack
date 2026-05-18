{
    "name": "Farm Water Source",
    "version": "19.0.1.0.0",
    "summary": "Wells, ponds, troughs, springs — geometry + which fields they serve",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/ledoent/farm-pack",
    "license": "AGPL-3",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_field_geo",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/farm_water_source_views.xml",
        "views/farm_water_source_menu.xml",
    ],
    "installable": True,
    "application": False,
}
