# F1 Telemetry Replay

A Formula 1 telemetry analysis and replay tool built with FastF1 and Plotly.

## Features

- Animated lap replay visualization
- Driver speed maps
- Driver vs. driver telemetry comparison
- Delta time analysis across a lap
- Segment-by-segment time gain/loss analysis
- Speed, Throttle, and Brake telemetry comparison
- Circuit corner markers
- Automatic team and driver coloring via FastF1
- Interactive Plotly dashboards

## Files

### replay.py
Animated lap replay around the circuit.

### comparison.py
Compare two drivers using:
- Speed
- Throttle
- Brake

### dashboard.py
Interactive telemetry dashboard containing:
- Delta time
- Speed comparison
- Throttle comparison
- Brake comparison
- Largest gain/loss segment analysis

### segment_analysis.py
Terminal-based segment gain/loss analysis between drivers.



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
drivers_to_compare = ['VER', 'RUS']
METRIC = 'Speed'
```
### delta_time.py:
```python
driver_compared = 'RUS'
reference_driver = 'VER'
```
## Installation
pip install -r requirements.txt
