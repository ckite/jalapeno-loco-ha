"""Sensor platform for Jalapeño Loco Specials."""
import logging
import re
from datetime import datetime
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

DOMAIN = "jalapeno_loco"
URL = "https://www.jalapenolocomilwaukee.com/weeklyspecials"
SCAN_INTERVAL_HOURS = 12
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    """Set up the Jalapeño Loco sensor platform."""
    async_add_entities([EeloteTamalesSensor(hass)], True)


class EeloteTamalesSensor(SensorEntity):
    """Sensor to track Elote Tamales availability."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = "Elote Tamales"
        self._attr_unique_id = "sensor.elote_tamales"
        self._attr_native_value = STATE_UNAVAILABLE
        self._available = False
        self._date_range = None
        self._date_range_end = None
        self._description = None
        self._price = None
        self._last_updated = None

    @property
    def state(self) -> str:
        """Return the state."""
        if self._available:
            return "available"
        return "unavailable"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "date_range": self._date_range,
            "end_date": self._date_range_end,
            "description": self._description,
            "price": self._price,
            "last_updated": self._last_updated,
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            headers = {"User-Agent": USER_AGENT}
            async with aiohttp.ClientSession() as session:
                async with session.get(URL, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    html = await response.text()

            # Parse the page
            soup = BeautifulSoup(html, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)

            # Extract date range from page (looks for "April 24th through May 7th" pattern)
            date_match = re.search(
                r"([A-Z][a-z]+\s+\d{1,2}[a-z]*)\s+(?:through|to)\s+([A-Z][a-z]+\s+\d{1,2}[a-z]*)",
                page_text,
                re.IGNORECASE,
            )

            if date_match:
                self._date_range = f"{date_match.group(1)} through {date_match.group(2)}"
                # Parse end date for cleaner attribute
                try:
                    end_date_str = date_match.group(2)
                    # Strip ordinal suffixes: "4th" -> "4", "22nd" -> "22", etc.
                    end_date_str = re.sub(r"(\d+)(?:st|nd|rd|th)\b", r"\1", end_date_str)
                    end_date = datetime.strptime(end_date_str, "%B %d").replace(year=datetime.now().year)
                    self._date_range_end = end_date.strftime("%Y-%m-%d")
                except ValueError:
                    self._date_range_end = None

            # Search for "elote tamales" (case-insensitive, same line)
            # Search for the tamales entry: match the item name, capture description + price.
            # Uses a non-greedy match up to 600 chars so we reach the price without
            # bleeding into the next menu item.
            entry_match = re.search(
                r"((?:elote\s+tamales|tamales\s+(?:de\s+)?elote).{10,600}?\$[\d.]+(?:\s*/\s*\$[\d.]+)?)",
                page_text,
                re.IGNORECASE | re.DOTALL,
            )
            found = entry_match is not None
            description_context = ""
            price = ""

            if found:
                full_entry = re.sub(r"\s+", " ", entry_match.group(1)).strip()
                description_context = full_entry
                # The last price in the captured entry is the tamales price
                all_prices = re.findall(r"\$[\d.]+(?:\s*/\s*\$[\d.]+)?", full_entry)
                if all_prices:
                    price = all_prices[-1]

            self._available = found
            if found and description_context:
                # Store description (first 200 chars)
                self._description = description_context[:200]
                # Store price separately
                if price:
                    self._price = price
                else:
                    self._price = None
            else:
                self._description = None
                self._price = None

            self._last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            _LOGGER.debug(
                "Elote Tamales sensor updated: available=%s, date_range=%s, price=%s",
                self._available,
                self._date_range,
                price,
            )

        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to fetch Jalapeño Loco specials page: %s", err)
            self._available = False
            self._last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as err:
            _LOGGER.error("Error updating Elote Tamales sensor: %s", err)
            self._available = False
            self._last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
