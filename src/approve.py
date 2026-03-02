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

TIMEOUT = (5, 15)

for component in COMPONENTS:
    print(f"\n=== {component} ===")

    units_url = f"{BASE}/translations/{PROJECT}/{component}/{LANG}/units/"
    params = {"q": "state:translated", "page_size": 500}

    try:
        r = requests.get(units_url, headers=HEADERS, params=params, timeout=TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        print(f"Error finding units: {e}")
        continue

    data = r.json()
    units = data.get("results", [])

    print(f"Found {len(units)} units to approve")

    approved_count = 0
    failed_count = 0

    for unit in units:
        uid = unit["id"]
        unit_url = f"{BASE}/units/{uid}/"

        payload = {
            "state": 30,
            "target": unit["target"]
        }

        try:
            rr = requests.patch(
                unit_url,
                headers={**HEADERS, "Content-Type": "application/json"},
                json=payload,
                timeout=TIMEOUT
            )

            if rr.status_code in (200, 201):
                print(f"Approved unit {uid}")
                approved_count += 1
            else:
                print(f"Failed to approve {uid}: status {rr.status_code} - {rr.text}")
                failed_count += 1

        except Exception as e:
            print(f"Error approving unit {uid}: {e}")
            failed_count += 1

        time.sleep(0.6)

    print(f"Summary for {component}: {approved_count} approved, {failed_count} failed")