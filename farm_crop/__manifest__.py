{
    "name": "Farm Crop Catalog",
    "summary": "Catalog of crops grown on the farm (lettuce, tomato, corn, etc.)",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/farm_crop_data.xml",
        "views/farm_crop_views.xml",
        "views/farm_crop_menu.xml",
    ],
    "demo": [
        "demo/farm_crop_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
