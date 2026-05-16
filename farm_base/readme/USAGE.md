To use the mixins in your own farm module, inherit them on your concrete model:

```python
class FarmYield(models.Model):
    _name = "farm.yield"
    _inherit = ["farm.measurement.mixin", "farm.gps.point.mixin"]
```

You then get `measurement_value`, `measurement_uom_id`, `gps_latitude`, and
`gps_longitude` for free, along with computed display strings and the
`measurement_to(target_uom)` helper.
