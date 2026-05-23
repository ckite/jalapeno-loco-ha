# Jalapeño Loco Specials Sensor for Home Assistant

Tracks availability of **Elote Tamales** from Jalapeño Loco's weekly specials page.

## Features

- **Sensor State**: `available` or `unavailable`
- **Attributes**:
  - `date_range`: Full date range of specials (e.g., "April 24th through May 7th")
  - `end_date`: Parsed end date (e.g., "2026-05-07")
  - `description`: Menu item description and details (first 200 chars)
  - `price`: Price of the item if found (e.g., "$12.95")
  - `last_updated`: Timestamp of last sensor update

- **Scheduled Updates**: Checks twice daily at 4 AM and 4 PM (configurable)
- **Flexible Matching**: Detects "elote tamales" case-insensitive, same line
- **Automatic Price Extraction**: Pulls price from menu item description

## Installation

### 1. Copy Files to Home Assistant

On your Home Assistant server, create the custom component directory:

```bash
mkdir -p /root/homeassistant/custom_components/jalapeno_loco
```

Copy the following files to that directory:
- `manifest.json`
- `__init__.py`
- `sensor.py`

### 2. Update Configuration

Add to your `configuration.yaml`:

```yaml
jalapeno_loco:
```

### 3. Add Automations (Optional but Recommended)

Add to your `configuration.yaml`:

```yaml
automation:
  - alias: "Update Elote Tamales Sensor - 4 AM"
    trigger:
      platform: time
      at: "04:00:00"
    action:
      service: homeassistant.update_entity
      target:
        entity_id: sensor.elote_tamales

  - alias: "Update Elote Tamales Sensor - 4 PM"
    trigger:
      platform: time
      at: "16:00:00"
    action:
      service: homeassistant.update_entity
      target:
        entity_id: sensor.elote_tamales
```

### 4. Restart Home Assistant

Via UI: **Settings** → **System** → **Restart**

Or command line:
```bash
docker exec homeassistant homeassistant-cli service homeassistant.restart
```

### 5. Verify the Sensor

Go to **Developer Tools** → **States** and search for `sensor.elote_tamales`. You should see:
- **State**: `available` or `unavailable`
- **Attributes**: date_range, end_date, description, price, last_updated

## Optional: Create a Friendly Template Sensor

Add to `configuration.yaml`:

```yaml
template:
  - sensor:
      - name: "Elote Tamales Status"
        unique_id: "sensor.elote_tamales_status"
        state: >
          {% if states('sensor.elote_tamales') == 'available' %}
            🌮 ELOTE TAMALES ARE AVAILABLE! 
            Price: {{ state_attr('sensor.elote_tamales', 'price') }}
            (through {{ state_attr('sensor.elote_tamales', 'end_date') }})
          {% else %}
            ❌ Elote Tamales not available. 
            Next specials: {{ state_attr('sensor.elote_tamales', 'date_range') }}
          {% endif %}
```

## Slack Notification

Once you verify the sensor works, create an automation in the UI:

**Trigger**: `sensor.elote_tamales` state changes to `available`
**Action**: Send Slack message

Example:
```yaml
automation:
  - alias: "Notify Slack - Elote Tamales Available"
    trigger:
      platform: state
      entity_id: sensor.elote_tamales
      to: "available"
    action:
      service: notify.slack
      data:
        message: |
          🌮 **ELOTE TAMALES ARE AVAILABLE!**
          Price: {{ state_attr('sensor.elote_tamales', 'price') }}
          Available through: {{ state_attr('sensor.elote_tamales', 'end_date') }}
          Details: {{ state_attr('sensor.elote_tamales', 'description') }}
```

## Troubleshooting

### Sensor Not Appearing

Check these in order:

1. **Verify files are in the right place:**
   ```bash
   ls -la /root/homeassistant/custom_components/jalapeno_loco/
   ```
   Should show: `__init__.py`, `sensor.py`, `manifest.json`

2. **Check for YAML syntax errors in configuration.yaml:**
   - UI: **Settings** → **System** → **Developer Tools** → **Check Configuration**
   - Or manually validate the `jalapeno_loco:` line is indented correctly

3. **Check Home Assistant logs for errors:**
   ```bash
   docker logs homeassistant | grep -i "jalapeno\|elote\|custom_components"
   ```
   Or via UI: **Settings** → **System** → **Logs**

4. **Force reload the integration:**
   - In Developer Tools → **States**, search for `sensor.elote_tamales`
   - If not there, try restarting HA again (changes to custom_components require restart)

5. **Check if the manifest has errors:**
   - Ensure `manifest.json` is valid JSON (no trailing commas)

### Common Issues

- **Sensor not appearing**: See "Sensor Not Appearing" section above
- **Request timeout**: Website may be slow; increase timeout in `sensor.py`
- **BeautifulSoup/aiohttp not found**: These are automatically installed via `requirements` in manifest.json

## Customization

### Change Check Times

Update automations to different times:
```yaml
at: "06:00:00"  # 6 AM
at: "14:00:00"  # 2 PM
```

### Change Menu Item

Edit `sensor.py` and replace the `entry_match` regex pattern with your own search term. The current pattern matches both "Elote Tamales" and "Tamales de Elote":
```python
entry_match = re.search(
    r"((?:elote\s+tamales|tamales\s+(?:de\s+)?elote).{10,600}?\$[\d.]+(?:\s*/\s*\$[\d.]+)?)",
    page_text,
    re.IGNORECASE | re.DOTALL,
)
```
Replace the alternation group with your item name, e.g. `(?:chile\s+relleno)` for Chile Relleno.

### Increase Request Timeout

If the website is slow or times out, increase the timeout in `sensor.py`:
```python
timeout=aiohttp.ClientTimeout(total=15)  # Change from 10 to 15 seconds
```

---

**URL**: https://www.jalapenolocomilwaukee.com/weeklyspecials
**Last Updated**: May 2026
