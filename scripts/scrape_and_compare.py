"""Scrape restaurants N times, compare deterministic hashes, and emit update artifacts."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# This allows importing `backend.*` from lunch-web-app despite the hyphen in folder name.
WEBAPP_ROOT = REPO_ROOT / "lunch-web-app"
if str(WEBAPP_ROOT) not in sys.path:
    sys.path.insert(0, str(WEBAPP_ROOT))

from backend.cached_menus import CACHED_RESTAURANTS
from backend.scraper.browse import browse_and_extract
from backend.scraper.search_restaurants import search_restaurant_url


@dataclass
class ScrapeRunResult:
    hash_sha256: str
    hash_md5: str
    items: list[dict[str, Any]]


def _clean_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.strip().split())


def _normalize_price_to_cents(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return int((amount * 100).to_integral_value())


def _normalize_item_for_hash(item: dict[str, Any]) -> tuple[str, int | None, str]:
    name = _clean_text(item.get("name")).lower()
    price_cents = _normalize_price_to_cents(item.get("price"))
    category = _clean_text(item.get("category") or "other").lower()
    return (name, price_cents, category)


def _normalize_item_for_storage(item: dict[str, Any]) -> dict[str, Any]:
    category = _clean_text(item.get("category") or "other").lower() or "other"
    return {
        "name": _clean_text(item.get("name")),
        "price": float(Decimal(str(item.get("price")))) if item.get("price") is not None else None,
        "category": category,
        "description": _clean_text(item.get("description")),
        "subcategory": _clean_text(item.get("subcategory")) or None,
    }


def _hash_items(items: list[dict[str, Any]]) -> tuple[str, str]:
    normalized_rows = [_normalize_item_for_hash(item) for item in items]
    normalized_rows.sort()
    payload = {
        "algorithm_version": 1,
        "items": normalized_rows,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    sha256_value = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    md5_value = hashlib.md5(serialized.encode("utf-8")).hexdigest()
    return sha256_value, md5_value


def _to_plain_scraped_items(extracted_items: list[Any]) -> list[dict[str, Any]]:
    plain: list[dict[str, Any]] = []
    for item in extracted_items:
        category = getattr(item, "category", "other")
        category_value = getattr(category, "value", category)
        plain.append(
            {
                "name": getattr(item, "name", ""),
                "price": getattr(item, "price", None),
                "category": category_value,
                "description": getattr(item, "description", ""),
                "subcategory": getattr(item, "subcategory", None),
            }
        )
    return plain


def _load_restaurants(config_path: Path) -> list[dict[str, Any]]:
    raw_text = config_path.read_text(encoding="utf-8")

    if config_path.suffix.lower() in {".yaml", ".yml"}:
        parsed = yaml.safe_load(raw_text)
    else:
        parsed = json.loads(raw_text)

    restaurants = parsed.get("restaurants", [])
    if not isinstance(restaurants, list):
        raise ValueError("restaurants config must contain a top-level 'restaurants' list")

    return [r for r in restaurants if r.get("enabled", True)]


def _load_hashes(hashes_path: Path) -> dict[str, Any]:
    if not hashes_path.exists():
        return {"version": 1, "hash_algorithm": "sha256", "restaurants": {}}
    return json.loads(hashes_path.read_text(encoding="utf-8"))


def _current_cached_menu_map() -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = {}
    for restaurant in CACHED_RESTAURANTS:
        name = str(restaurant["restaurant_name"])
        items = []
        for item in restaurant["items"]:
            items.append(
                {
                    "name": item.name,
                    "price": float(item.price) if item.price is not None else None,
                    "category": item.category,
                    "description": item.description,
                    "subcategory": item.subcategory,
                }
            )
        data[name] = items
    return data


def _change_summary(old_items: list[dict[str, Any]], new_items: list[dict[str, Any]]) -> dict[str, Any]:
    old_map = {
        (_clean_text(item.get("name")).lower(), _clean_text(item.get("category") or "other").lower()): _normalize_price_to_cents(item.get("price"))
        for item in old_items
    }
    new_map = {
        (_clean_text(item.get("name")).lower(), _clean_text(item.get("category") or "other").lower()): _normalize_price_to_cents(item.get("price"))
        for item in new_items
    }

    old_keys = set(old_map)
    new_keys = set(new_map)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    price_changed = sorted(k for k in old_keys & new_keys if old_map[k] != new_map[k])

    base = max(len(old_keys), 1)
    ratio = (len(added) + len(removed) + len(price_changed)) / base

    return {
        "added_count": len(added),
        "removed_count": len(removed),
        "price_changed_count": len(price_changed),
        "change_ratio": ratio,
        "added_examples": [f"{k[0]} ({k[1]})" for k in added[:5]],
        "removed_examples": [f"{k[0]} ({k[1]})" for k in removed[:5]],
        "price_changed_examples": [f"{k[0]} ({k[1]})" for k in price_changed[:5]],
    }


async def _scrape_once(restaurant_name: str, known_url: str | None) -> ScrapeRunResult:
    start_url = known_url
    if not start_url:
        start_url = await search_restaurant_url(restaurant_name)

    _, extracted_items = await browse_and_extract(restaurant_name, start_url)
    plain_items = _to_plain_scraped_items(extracted_items)
    normalized_items = [_normalize_item_for_storage(item) for item in plain_items]
    hash_sha256, hash_md5 = _hash_items(normalized_items)
    return ScrapeRunResult(hash_sha256=hash_sha256, hash_md5=hash_md5, items=normalized_items)


async def run(args: argparse.Namespace) -> int:
    restaurants = _load_restaurants(Path(args.config))
    hashes_db = _load_hashes(Path(args.hashes))
    old_hashes: dict[str, str] = hashes_db.get("restaurants", {})

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cached_map = _current_cached_menu_map()
    final_menu_map = dict(cached_map)
    updated_hashes = dict(old_hashes)

    report: dict[str, Any] = {
        "consensus_policy": "strict_majority",
        "default_runs": args.runs,
        "restaurants": [],
        "menus_updated": False,
        "should_notify": False,
        "has_errors": False,
        "has_significant_changes": False,
    }

    for restaurant in restaurants:
        name = str(restaurant.get("name", "")).strip()
        if not name:
            continue

        known_url = restaurant.get("known_url")
        run_count = int(restaurant.get("scrape_runs") or args.runs)
        if run_count < 3:
            run_count = 3
        if run_count % 2 == 0:
            run_count += 1

        successes: list[ScrapeRunResult] = []
        errors: list[str] = []

        for index in range(run_count):
            try:
                result = await _scrape_once(name, known_url)
                successes.append(result)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"run_{index + 1}: {type(exc).__name__}: {exc}")

        restaurant_report: dict[str, Any] = {
            "restaurant_name": name,
            "configured_runs": run_count,
            "success_runs": len(successes),
            "failed_runs": len(errors),
            "errors": errors,
            "status": "error",
            "changed": False,
            "significant_change": False,
        }

        if not successes:
            restaurant_report["status"] = "no_successful_scrapes"
            report["has_errors"] = True
            report["should_notify"] = True
            report["restaurants"].append(restaurant_report)
            continue

        hash_counts = Counter(result.hash_sha256 for result in successes)
        winner_hash, winner_count = hash_counts.most_common(1)[0]
        required = math.ceil(run_count / 2)

        restaurant_report["hash_counts"] = dict(hash_counts)
        restaurant_report["required_for_consensus"] = required

        if winner_count < required:
            restaurant_report["status"] = "no_majority"
            report["has_errors"] = True
            report["should_notify"] = True
            report["restaurants"].append(restaurant_report)
            continue

        winner_result = next(item for item in successes if item.hash_sha256 == winner_hash)
        old_hash = old_hashes.get(name)
        changed = old_hash != winner_hash

        restaurant_report["status"] = "consensus"
        restaurant_report["accepted_hash_sha256"] = winner_hash
        restaurant_report["accepted_hash_md5"] = winner_result.hash_md5
        restaurant_report["changed"] = changed

        if errors:
            # A consensus with failed attempts is still useful but worth notifying.
            report["has_errors"] = True
            report["should_notify"] = True

        if changed:
            old_items = cached_map.get(name, [])
            change = _change_summary(old_items, winner_result.items)
            significant = change["change_ratio"] > args.significant_threshold
            restaurant_report["change_summary"] = change
            restaurant_report["significant_change"] = significant

            if significant:
                report["has_significant_changes"] = True
                report["should_notify"] = True
            else:
                final_menu_map[name] = winner_result.items
                updated_hashes[name] = winner_hash
                report["menus_updated"] = True

        report["restaurants"].append(restaurant_report)

    canonical_data = {
        "restaurants": [
            {
                "restaurant_name": name,
                "items": items,
            }
            for name, items in sorted(final_menu_map.items(), key=lambda x: x[0].lower())
        ]
    }

    next_hashes = {
        "version": 1,
        "hash_algorithm": "sha256",
        "restaurants": dict(sorted(updated_hashes.items(), key=lambda x: x[0].lower())),
    }

    (out_dir / "menus_canonical.json").write_text(
        json.dumps(canonical_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "menu_hashes.next.json").write_text(
        json.dumps(next_hashes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if args.apply:
        Path(args.hashes).write_text(
            json.dumps(next_hashes, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape menus and compare deterministic hashes")
    parser.add_argument(
        "--config",
        default="lunch-web-app/automation/restaurants.yml",
        help="YAML or JSON restaurant config",
    )
    parser.add_argument(
        "--hashes",
        default="lunch-web-app/automation/menu_hashes.json",
        help="Path to current hash store",
    )
    parser.add_argument("--runs", type=int, default=3, help="Default scrape runs per restaurant (odd numbers preferred)")
    parser.add_argument(
        "--significant-threshold",
        type=float,
        default=0.25,
        help="Mark change as significant when ratio exceeds this threshold",
    )
    parser.add_argument("--output-dir", default=".menu-artifacts", help="Artifact output directory")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write menu_hashes.json in-place with accepted hash updates",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
