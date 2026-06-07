# F1 Telemetry Replay

A Formula 1 telemetry replay tool built with FastF1 and Plotly.

## Features

- Animated lap replay visualization
- Driver speed maps
- Driver vs. driver telemetry comparison
- Support for Speed, Throttle, Brake, RPM, and other telemetry channels
- Circuit corner markers
- Automatic team/driver coloring via FastF1

## Configuration

Edit the following variables in the script:

```python
YEAR = 2026
SESSION_NAME = 'Australian Grand Prix'
SESSION_TYPE = 'R'
lap_number = 11
drivers_to_compare = ['VER', 'NOR']
METRIC = 'Speed'