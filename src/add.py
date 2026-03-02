import os
import requests
from pathlib import Path

TOKEN = os.getenv("WEBLATE_TOKEN")
BASE = "https://weblate.equicord.org/api/translations/equicord/{component}/pt_BR/file/" # just an example

FILES = {
    "equicord": Path("path/to/weblate/branch/language/file.json"),
    "vencord": Path("path/to/weblate/branch/language/file.json"),
}

headers = {"Authorization": f"Token {TOKEN}"}

for component, file_path in FILES.items():
    url = BASE.format(component=component)
    with file_path.open("rb") as f:
        r = requests.put(
            url,
            headers=headers,
            files={"file": (file_path.name, f, "application/json")},
            data={
                "method": "approve",
                "author_name": "Friend",
                # optional:
                # "conflicts": "replace-translated",
            },
            timeout=120,
        )
    print(f"[{component}] status={r.status_code}")
    try:
        print(r.json())
    except Exception:
        print(r.text[:500])