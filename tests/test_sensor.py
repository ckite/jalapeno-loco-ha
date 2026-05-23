"""Pytest tests for the Jalapeño Loco sensor parsing logic."""
import re
from pathlib import Path

from bs4 import BeautifulSoup

FIXTURES = Path(__file__).parent / "fixtures"


def parse_page(html: str) -> dict:
    """Run the sensor parsing logic against raw HTML. Mirrors sensor.py async_update."""
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(separator=" ", strip=True)

    date_range = None
    date_match = re.search(
        r"([A-Z][a-z]+\s+\d{1,2}[a-z]*)\s+(?:through|to)\s+([A-Z][a-z]+\s+\d{1,2}[a-z]*)",
        page_text,
        re.IGNORECASE,
    )
    if date_match:
        date_range = f"{date_match.group(1)} through {date_match.group(2)}"

    entry_match = re.search(
        r"((?:elote\s+tamales|tamales\s+(?:de\s+)?elote).{10,600}?\$[\d.]+(?:\s*/\s*\$[\d.]+)?)",
        page_text,
        re.IGNORECASE | re.DOTALL,
    )
    found = entry_match is not None
    price = None
    description = None

    if found:
        full_entry = re.sub(r"\s+", " ", entry_match.group(1)).strip()
        description = full_entry[:200]
        all_prices = re.findall(r"\$[\d.]+(?:\s*/\s*\$[\d.]+)?", full_entry)
        if all_prices:
            price = all_prices[-1]

    return {"found": found, "price": price, "description": description, "date_range": date_range}


def test_elote_tamales_on_menu():
    """Tamales de Elote are a special — sensor should report available with correct price."""
    html = (FIXTURES / "weeklyspecials.html").read_text(encoding="utf-8")
    result = parse_page(html)

    assert result["found"], "Expected elote tamales to be found"
    assert result["price"] == "$8.95", f"Expected $8.95, got {result['price']}"
    assert result["date_range"] == "May 22nd through June 4th"


def test_no_tamales_on_menu():
    """No tamales at all this week — sensor should report unavailable."""
    html = (FIXTURES / "weeklyspecials_no_tamales.html").read_text(encoding="utf-8")
    result = parse_page(html)

    assert not result["found"], "Expected elote tamales NOT to be found"
    assert result["price"] is None


def test_shrimp_tamales_not_elote():
    """Shrimp tamales are on the menu but NOT elote tamales — should not false-positive."""
    html = (FIXTURES / "weeklyspecials_shrimp_tamales.html").read_text(encoding="utf-8")
    result = parse_page(html)

    assert not result["found"], "Shrimp tamales should not trigger elote tamales detection"
    assert result["price"] is None
