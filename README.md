# Satellite Brightness Calculator

Calculate and visualize satellite brightness based on solar panel power requirements and viewing geometry.


Requires: `lumos` library and `starlink` satellite models

## Usage

```python
from satellite_brightness import calculate_brightness

result = calculate_brightness(
    sat_height=550e3,      # Satellite altitude in meters (550 km)
    sat_altitude=45,       # Viewing angle above horizon in degrees (0-90°)
    sat_azimuth=270,       # Direction to satellite: 0°=North, 90°=East, 180°=South, 270°=West
    sun_altitude=-15,      # Sun angle below horizon in degrees (negative = below horizon)
    sun_azimuth=270,       # Direction to sun: 0°=North, 90°=East, 180°=South, 270°=West
    power_kw=100,          # Satellite power requirement in kilowatts
    continuous=False       # False = instantaneous power, True = continuous 24/7 power (doubles panel area)
)

print(result)
# Output: {'intensity': array([8.92e-11]), 'ab_magnitude': array([5.90]), 'area': 419.84, 'power_type': 'instantaneous'}
```

## Parameter Explanations

### `sat_height` (meters)
The orbital altitude of the satellite above Earth's surface.
- **Example**: `550e3` = 550 km (typical Starlink altitude)
- **Example**: `1000e3` = 1,000 km

### `sat_altitude` (degrees, 0-90°)
How high the satellite appears above your horizon.
- **0°** = On the horizon
- **45°** = Halfway between horizon and zenith
- **90°** = Directly overhead (zenith)

### `sat_azimuth` (degrees, 0-360°)
The compass direction to the satellite.
- **0°** = North
- **90°** = East  
- **180°** = South
- **270°** = West

### `sun_altitude` (degrees)
How high the sun is above (+) or below (-) the horizon.
- **Positive values**: Sun is above horizon (daytime)
- **Negative values**: Sun is below horizon (twilight/night)
- **-6° to 0°**: Civil twilight
- **-12° to -6°**: Nautical twilight
- **-18° to -12°**: Astronomical twilight
- **Below -18°**: Astronomical darkness

### `sun_azimuth` (degrees, 0-360°)
The compass direction to the sun (same convention as `sat_azimuth`).

### `power_kw` (kilowatts)
The electrical power requirement of the satellite.
- Determines the size of solar panels needed
- **100 kW** → 419.84 m² of solar panels (instantaneous)
- **100 kW** → 839.68 m² of solar panels (continuous)

### `continuous` (True/False)
Power generation mode:
- **False** (default): Instantaneous power - panels sized for peak sunlight
- **True**: Continuous power - panels sized for 24/7 operation (doubles the area)

### Optional Parameters

- `include_sun=True`: Include direct sunlight reflection
- `include_earthshine=False`: Include light reflected from Earth
- `earth_panel_density=151`: Resolution for Earth reflection calculations
- `earth_brdf=None`: Earth surface reflection model (uses default PHONG if None)

## Understanding the Results

The function returns a dictionary with:

- **`intensity`**: Raw brightness value in physical units
- **`ab_magnitude`**: Brightness in astronomical magnitude system
  - Lower values = brighter
  - **~3-4**: Very bright, easily visible to naked eye
  - **~6**: Naked eye limit under dark skies
  - **~8-9**: Binoculars needed
  - **12.5**: Effectively invisible (zero intensity)
- **`area`**: Solar panel area in m²
- **`power_type`**: 'instantaneous' or 'continuous'
