from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import sys
from pathlib import Path


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_REPO_ROOT = Path(__file__).resolve().parents[1]
sac = _load_module("scrape_and_compare", _REPO_ROOT / "scripts" / "scrape_and_compare.py")
generate_cached_menus = _load_module(
    "generate_cached_menus",
    _REPO_ROOT / "scripts" / "generate_cached_menus.py",
).generate_cached_menus


class _FakeItem:
    def __init__(self, name: str, price: float, category: str, description: str, subcategory: str | None = None):
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.subcategory = subcategory


async def _fake_search_restaurant_url(restaurant_name: str, city: str = "Malm\u00f6") -> str:
    return f"https://example.invalid/{restaurant_name.lower().replace(' ', '-')}/{city.lower()}"


async def _fake_browse_and_extract(restaurant_name: str, start_url: str):
    _ = (restaurant_name, start_url)
    items = [
        _FakeItem("Chicken Bowl", 129, "main", "Warm chicken bowl with rice."),
        _FakeItem("Sparkling Water", 22, "drink", "Cold sparkling water."),
    ]
    return "https://example.invalid/menu", items


def test_menu_pipeline_e2e(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "restaurants.yml"
    hashes_path = tmp_path / "menu_hashes.json"
    out_dir = tmp_path / "artifacts"
    generated_cache = tmp_path / "cached_menus.py"

    config_path.write_text(
        """
restaurants:
  - name: E2E Bistro
    enabled: true
""".strip()
        + "\n",
        encoding="utf-8",
    )
    hashes_path.write_text(
        json.dumps({"version": 1, "hash_algorithm": "sha256", "restaurants": {}}, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(sac, "search_restaurant_url", _fake_search_restaurant_url)
    monkeypatch.setattr(sac, "browse_and_extract", _fake_browse_and_extract)

    args = argparse.Namespace(
        config=str(config_path),
        hashes=str(hashes_path),
        runs=3,
        significant_threshold=100.0,
        output_dir=str(out_dir),
        apply=False,
    )

    exit_code = asyncio.run(sac.run(args))
    assert exit_code == 0

    report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    assert report["menus_updated"] is True
    assert report["has_errors"] is False
    assert report["restaurants"][0]["status"] == "consensus"

    generate_cached_menus(out_dir / "menus_canonical.json", generated_cache)
    generated_text = generated_cache.read_text(encoding="utf-8")
    assert "CACHED_RESTAURANTS" in generated_text
    assert "Chicken Bowl" in generated_text
