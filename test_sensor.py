"""Manual debug script — hits the live URL and prints results.
Run directly: python3 test_sensor.py
Automated tests live in tests/test_sensor.py
"""
import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

URL = "https://www.jalapenolocomilwaukee.com/weeklyspecials"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


async def debug():
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(separator=" ", strip=True)

    print("\n--- PAGE TEXT SNIPPET (first 1000 chars) ---")
    print(page_text[:1000])
    print("--- END SNIPPET ---\n")

    words = page_text.split()
    print("--- TAMALES/ELOTE MENTIONS ---")
    for i, word in enumerate(words):
        if re.search(r"tamale|elote", word, re.IGNORECASE):
            context = " ".join(words[max(0, i - 5) : i + 15])
            print(f"  [{i}] ...{context}...")
    print("--- END MENTIONS ---\n")

    entry_match = re.search(
        r"((?:elote\s+tamales|tamales\s+(?:de\s+)?elote).{10,600}?\$[\d.]+(?:\s*/\s*\$[\d.]+)?)",
        page_text,
        re.IGNORECASE | re.DOTALL,
    )
    found = entry_match is not None
    price = None

    if found:
        full_entry = re.sub(r"\s+", " ", entry_match.group(1)).strip()
        all_prices = re.findall(r"\$[\d.]+(?:\s*/\s*\$[\d.]+)?", full_entry)
        price = all_prices[-1] if all_prices else None
        print(f"Description: {full_entry[:200]}")

    print(f"Found:       {found}")
    print(f"Price:       {price}")


if __name__ == "__main__":
    asyncio.run(debug())

