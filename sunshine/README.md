# Sunshine

UMDCTF 2025, OSINT. A garbage truck photographed in Summit County, Ohio with house number 356
in the background. The flag is the full address.

## Solve

The truck carried an Akron city marking, and the challenge named Summit County. Summit County
publishes an address-point layer through its public ArcGIS server, so rather than hunt the
street view by eye I queried it directly. `find-356.py` first lists the layer's fields, then
queries `ADDR_NUM = '356' AND UPPER(CITY) = 'AKRON'`:

```python
BASE_URL = "https://scgis.summitoh.net/hosted/rest/services/AddressPoints_DBC/FeatureServer"
where = "ADDR_NUM = '356' AND UPPER(CITY) = 'AKRON'"
```

Among the handful of results, the one matching the truck's street was 356 Hillwood Dr.

## Flag

```text
UMDCTF{356 Hillwood Dr, Akron, OH 44320}
```

## Files

```text
find-356.py   queries the Summit County GIS for house number 356 in Akron
```
