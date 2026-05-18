{
    "name": "Farm Fence",
    "version": "19.0.1.0.0",
    "summary": "Fence lines + condition tracking + auto-computed length",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/ledoent/farm-pack",
    "license": "AGPL-3",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_field_geo",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/farm_fence_views.xml",
        "views/farm_fence_menu.xml",
    ],
    "installable": True,
    "application": False,
}
