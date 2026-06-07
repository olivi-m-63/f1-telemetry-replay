# F1 Telemetry Replay

A Formula 1 telemetry analysis and replay tool built with FastF1 and Plotly.

## Features

- Animated lap replay visualization
- Driver speed maps
- Driver vs. driver telemetry comparison
- Support for Speed, Throttle, Brake, RPM, and other telemetry channels
- Circuit corner markers
- Automatic team/driver coloring via FastF1
- Delta time analysis across a lap

## How to Use

Edit the following variables in the script:

### All Files:
```python
YEAR = 2026
SESSION_NAME = 'Australian Grand Prix'
SESSION_TYPE = 'R'
lap_number = 11
```
### comparison.py:
```python
drivers_to_compare = ['VER', 'NOR']
METRIC = 'Speed'
```
### delta_time.py:
```python
driver_compared = 'RUS'
reference_driver = 'VER'
```
## Installation
pip install -r requirements.txt
