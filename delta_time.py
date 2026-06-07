import fastf1
import fastf1.plotting
import plotly.graph_objects as go
import pandas as pd
import numpy as np

fastf1.Cache.enable_cache(r'c:\\Users\\olivi\\python\\fastf1.cache')
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
fig = go.Figure()
fig.add_trace(go.Scatter(x=common_distance, y=delta_time, mode='lines', line=dict(width=2, color=fastf1.plotting.get_driver_color(driver_compared, session)), name=f"{driver_compared} vs {reference_driver} Delta Time"))     #add a trace for the delta time comparison between the two drivers

circuit_info = session.get_circuit_info()

for _, corner in circuit_info.corners.iterrows():

    fig.add_vline(
        x=corner['Distance'],
        line_width=1,
        line_dash='dot'
    )

    fig.add_annotation(
        x=corner['Distance'],
        y=1,
        yref='paper',
        text=f"T{corner['Number']}",
        showarrow=False,
        yshift=10
    )

fig.update_layout(
    title=f"{driver_compared} vs {reference_driver} Delta Time Comparison of Lap {lap_number} - {SESSION_NAME} {YEAR}",
    legend=dict(x=1.1, y=1.0),
    margin=dict(l=.3,r=300, t=50, b=0),
    template='ggplot2'

)


fig.update_yaxes(
    title_text="Delta Time (s)",
    nticks=10,
    showgrid=False
)
fig.update_xaxes(
    title_text="Distance (m)",
    showgrid = True
)


def format_time(timedelta):
    if pd.isna(timedelta):
        return "N/A"
    minutes=timedelta.seconds // 60
    seconds = timedelta.seconds % 60
    milliseconds =int(timedelta.microseconds) // 1000
    if minutes > 0:
        return f"{minutes}:{seconds}.{milliseconds:03d}"
    else:
        return f"{seconds}.{milliseconds:03d}"


fig.add_annotation(x=1.27, y=.8,xref='paper', yref = 'paper', text = f"{driver_compared} LAP TIME: {format_time(driver_compared_lap['LapTime'])}",showarrow=False, font = dict(color=fastf1.plotting.get_driver_color(driver_compared, session),size=14))
fig.add_annotation(x=1.27, y=(.8-.046),xref='paper', yref = 'paper', text = f"{reference_driver} LAP TIME: {format_time(reference_driver_lap['LapTime'])}",showarrow=False, font = dict(color=fastf1.plotting.get_driver_color(reference_driver, session),size=14))
fig.add_annotation(x=1.27, y=(.8-.092),xref='paper', yref = 'paper', text = f"Δ = {driver_compared} - {reference_driver}<br>+ = {driver_compared} behind<br>− = {driver_compared} ahead",showarrow=False, font = dict(color='black',size=14))

fig.show()
