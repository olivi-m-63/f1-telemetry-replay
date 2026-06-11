import fastf1
import fastf1.plotting
import plotly.graph_objects as go
import pandas as pd
import numpy as np

fastf1.Cache.enable_cache(r'c:\\Users\\olivi\\python\\fastf1.cache')        #replace with your desired cache directory
#change these to set the year, session name, and session type
YEAR = 2026
SESSION_NAME = 'Australian Grand Prix'
SESSION_TYPE = 'R'

lap_number = 11     #set the lap number to analyze for the session

session = fastf1.get_session(YEAR, SESSION_NAME, SESSION_TYPE)
session.load()

driver_compared = 'RUS'    #set the driver to compare against the reference driver by their three-letter code, e.g. 'HAM' for Lewis Hamilton, 'VER' for Max Verstappen, etc.
reference_driver = 'VER'     #set the reference driver for delta time comparison by their three-letter code, e.g. 'HAM' for Lewis Hamilton, 'VER' for Max Verstappen, etc.

driver_compared_lap_selection = session.laps.pick_driver(driver_compared)     #get the lap data for the driver to compare
if len(driver_compared_lap_selection) < lap_number:
    raise ValueError(f"{driver_compared} does not have enough laps in the session to analyze lap {lap_number}")
driver_compared_lap = driver_compared_lap_selection.iloc[lap_number-1]

telemetry_compared = driver_compared_lap.get_telemetry()     #get the telemetry data for the driver to compare


reference_driver_lap_selection = session.laps.pick_driver(reference_driver)     #get the lap data for the reference driver
if len(reference_driver_lap_selection) < lap_number:
    raise ValueError(f"{reference_driver} does not have enough laps in the session to analyze lap {lap_number}")

reference_driver_lap = reference_driver_lap_selection.iloc[lap_number-1]
telemetry_reference = reference_driver_lap.get_telemetry()     #get the telemetry data for the reference driver


common_distance = np.linspace(0, min(telemetry_compared['Distance'].max(), telemetry_reference['Distance'].max()), 5000)     #create a new distance array for the telemetry data to ensure both drivers have the same distance points for comparison
compared_time = np.interp(
    common_distance,
    telemetry_compared['Distance'],
    telemetry_compared['Time'].dt.total_seconds()
)     #interpolate the time values for the driver to compare at the new distance points

reference_time = np.interp(
    common_distance,
    telemetry_reference['Distance'],
    telemetry_reference['Time'].dt.total_seconds()
)     #interpolate the time values for the reference driver at the new distance points

delta_time = compared_time - reference_time     #calculate the delta time between the two drivers at each distance point


circuit_info = session.get_circuit_info()
corner_deltas = []
segment_results = []
for _, corner in circuit_info.corners.iterrows():       # type: ignore
    corner_idx = np.argmin(
        np.abs(common_distance - corner['Distance'])
    )
    corner_deltas.append(delta_time[corner_idx])
turn1_gain = corner_deltas[0] - 0
segment_results.append((f"Start → T1", turn1_gain))

for i in range(1, len(corner_deltas)):
    segment_results.append((f"T{i} → T{i+1}", corner_deltas[i] - corner_deltas[i-1]))

finish_delta = delta_time[-1]
segment_results.append(
    (f"T{len(corner_deltas)} → Finish",finish_delta - corner_deltas[-1]))

largest_losses = sorted(segment_results, key=lambda x: x[1], reverse=True)
largest_gains = sorted(segment_results, key=lambda x: x[1], reverse=False)

print("\nLargest gains:")
for segment, gain in largest_gains[:3]:
    print(f"{segment}: {gain:+.3f}s")

print("\nLargest losses:")
for segment, gain in largest_losses[:3]:
    print(f"{segment}: {gain:+.3f}s")

    


