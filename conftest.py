"""Stub out homeassistant so pytest can import __init__.py without HA installed."""
import sys
from unittest.mock import MagicMock

_HA_MODULES = [
    "homeassistant",
    "homeassistant.const",
    "homeassistant.core",
    "homeassistant.helpers",
    "homeassistant.helpers.discovery",
    "homeassistant.helpers.aiohttp_client",
]

for _mod in _HA_MODULES:
    sys.modules.setdefault(_mod, MagicMock())
