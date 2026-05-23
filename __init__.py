"""Jalapeño Loco Specials integration."""
import logging
from datetime import timedelta

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform

DOMAIN = "jalapeno_loco"
PLATFORMS = [Platform.SENSOR]
SCAN_INTERVAL = timedelta(hours=12)  # Update twice daily

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Jalapeño Loco integration from configuration.yaml."""
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        # Load the sensor platform
        hass.async_create_task(
            async_load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)
        )
    
    return True
