#!/usr/bin/env python3
import requests, sys

BASE_URL = "https://scgis.summitoh.net/hosted/rest/services/AddressPoints_DBC/FeatureServer"

print("🚀 find-356.py running…")

def inspect_fields():
    url = f"{BASE_URL}/0"
    resp = requests.get(url, params={"f": "pjson"})
    print("→ GET", resp.url)
    print("  Status:", resp.status_code)
    print("  Content-Type:", resp.headers.get("Content-Type"))
    preview = resp.text.replace("\n"," ")[:200]
    print("  Body preview:", repr(preview), "...\n")

    try:
        info = resp.json()
    except ValueError as e:
        print("❌ JSON parse error:", e)
        sys.exit(1)

    if "fields" not in info:
        print("❌ No 'fields' key. Keys:", list(info.keys()))
        sys.exit(1)

    print(f"✔ Found {len(info['fields'])} fields:")
    for fld in info["fields"]:
        print("  •", fld["name"], f"({fld['type']})")
    print()

def fetch_356_addresses():
    """Query ADDR_NUM = '356' and CITY = 'AKRON' using the real field names."""
    url = f"{BASE_URL}/0/query"
    where = "ADDR_NUM = '356' AND UPPER(CITY) = 'AKRON'"
    params = {
        "where": where,
        "outFields": "ADDR_NUM,PRE_DIR,PRE_TYPE,STR_NAME,STR_TYPE,SUF_DIR,CITY,STATE,ZIP",
        "f": "pjson",
        "resultRecordCount": 2000,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    if "features" not in data:
        print("❌ No 'features' key. Keys:", list(data.keys()))
        sys.exit(1)

    def build_street(a):
        parts = [
            a.get("PRE_DIR") or "",
            a.get("STR_NAME") or "",
            a.get("STR_TYPE") or "",
            a.get("SUF_DIR") or ""
        ]
        return " ".join(p for p in parts if p).strip()

    seen = set()
    for feat in data["features"]:
        a = feat["attributes"]
        street = build_street(a)
        addr = f"{a['ADDR_NUM']} {street}, {a['CITY']}, {a['STATE']} {a['ZIP']}, USA"
        seen.add(addr)

    print("🏠 356 addresses in Akron:")
    for addr in sorted(seen):
        print("  ", addr)

if __name__ == "__main__":
    inspect_fields()
    fetch_356_addresses()   
