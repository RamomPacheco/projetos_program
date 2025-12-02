from __future__ import annotations

import json
from typing import Any, Dict


def save_data_to_json(data: Dict[str, Any], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_data_from_json(output_path: str) -> Dict[str, Any]:
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
