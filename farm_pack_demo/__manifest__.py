{
    "name": "Farm Pack Demo",
    "summary": "Showcase dataset for the farm pack — partners, products, "
    "coops, CSA, routes, fields with polygons, observations, fences, water",
    "version": "19.0.1.1.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_pack",
    ],
    "data": [],
    # Demo files must load in dependency order — partners first (referenced
    # by everyone), then geo fields (referenced by observation/water/fence).
    "demo": [
        "demo/res_partner_demo.xml",
        "demo/product_demo.xml",
        "demo/farm_coop_demo.xml",
        "demo/farm_egg_collection_demo.xml",
        "demo/farm_csa_demo.xml",
        "demo/farm_delivery_demo.xml",
        "demo/farm_market_demo.xml",
        "demo/farm_qbo_demo.xml",
        "demo/farm_field_geo_demo.xml",
        "demo/farm_observation_demo.xml",
        "demo/farm_water_source_demo.xml",
        "demo/farm_fence_demo.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
