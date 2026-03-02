import os
import requests
import time

TOKEN = os.getenv("WEBLATE_TOKEN")
if not TOKEN:
    raise RuntimeError("WEBLATE_TOKEN is not defined")

BASE = "https://weblate.equicord.org/api" # select your weblate here
PROJECT = "equicord" # select your project here
LANG = "pt_BR" # select your lang here 
COMPONENTS = ["equicord", "vencord", "api", "translation"] # select your components here

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Accept": "application/json"
}

TIMEOUT = (10, 30)

def get_all_units(component):
    units = []
    url = f"{BASE}/translations/{PROJECT}/{component}/{LANG}/units/"
    params = {"page_size": 2000}  # max ig

    while url:
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
            units.extend(data.get("results", []))
            url = data.get("next")
            params = {}
            print(f"Loaded {len(units)} units so far...")
            time.sleep(1.5)
        except requests.exceptions.HTTPError as e:
            if r and r.status_code == 429:
                print("Rate limit → waiting 60s")
                time.sleep(60)
                continue
            print(f"Error: {e}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    return units

total_rejected = 0

for component in COMPONENTS:
    print(f"\n=== {component} ===")
    units = get_all_units(component)
    print(f"Found {len(units)} units (with high page_size)")

    rejected = 0
    for idx, unit in enumerate(units, 1):
        uid = unit["id"]
        print(f"Unit {uid} ({idx}/{len(units)})")

        try:
            detail = requests.get(f"{BASE}/units/{uid}/", headers=HEADERS, timeout=TIMEOUT).json()
            sugs = detail.get("suggestions", [])
            if not sugs:
                continue

            print(f"{len(sugs)} suggestions")
            for sug in sugs:
                sug_id = sug["id"]
                resp = requests.delete(f"{BASE}/suggestions/{sug_id}/", headers=HEADERS, timeout=TIMEOUT)
                if resp.status_code in (200, 204):
                    print(f"Rejected {sug_id}")
                    rejected += 1
                    total_rejected += 1
                else:
                    print(f"Failed {sug_id}: {resp.status_code} {resp.text}")
                time.sleep(0.7)
        except Exception as e:
            print(f"Error in unit {uid}: {e}")

        time.sleep(1.2)

    print(f"Summary {component}: {rejected} rejected")

print(f"\nTotal rejected: {total_rejected}")