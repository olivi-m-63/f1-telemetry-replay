import fastf1
import fastf1.plotting
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
fastf1.Cache.enable_cache(r'c:\\Users\\olivi\\python\\fastf1.cache') #replace with your desired cache directory
#change these to set the year, session name, and session type
YEAR = 2026
SESSION_NAME = 'Australian Grand Prix'
SESSION_TYPE = 'R'
lap_number = 11     #set the lap number to analyze for the session

driver_compared = 'RUS'    #set the driver to compare against the reference driver by their three-letter code, e.g. 'HAM' for Lewis Hamilton, 'VER' for Max Verstappen, etc.
reference_driver = 'VER'     #set the reference driver for delta time comparison by their three-letter code, e.g. 'HAM' for Lewis Hamilton, 'VER' for Max Verstappen, etc.



session = fastf1.get_session(YEAR, SESSION_NAME, SESSION_TYPE)
session.load()

drivers_to_compare = [driver_compared, reference_driver]



def get_driver_telemetry(session, driver, lap_number):       #get telemetry for a specific driver and lap number
    laps = session.laps.pick_driver(driver)
    if len(laps) < (lap_number):
        return None,None
    lap = laps.iloc[lap_number-1]
    telemetry = lap.get_telemetry()
    return telemetry, lap       #return telemetry and lap data for the specified driver and lap number, or None if the driver doesn't have enough laps


telemetry_data = {}     #initialize dictionaries to store telemetry and lap data for each driver
lap_data = {}
for driver in drivers_to_compare:      #store telemetry and lap data in dictionaries
    telemetry, lap = get_driver_telemetry(session, driver, lap_number)
    if telemetry is None:       #if the driver doesn't have enough laps, skip to the next driver
        continue
    telemetry_data[driver] = telemetry
    lap_data[driver] = lap



telemetry_compared = telemetry_data[driver_compared]     #get the telemetry data for the driver to compare
telemetry_reference = telemetry_data[reference_driver]     #get the telemetry data for the reference driver


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

fig = make_subplots(
    rows=4, cols=1,shared_xaxes=True, 
    subplot_titles=(
        "Delta Time",
        "Speed",
        "Throttle",
        "Brake"
    ),
    vertical_spacing=0.02
)


fig.add_trace(go.Scatter(x=common_distance, y=delta_time, mode='lines', line=dict(width=2, color="#C35DFF"), name=f"{driver_compared} - {reference_driver}"), row=1,col=1)
fig.add_trace(go.Scatter(x=telemetry_data[driver_compared]['Distance'], y=telemetry_data[driver_compared]['Speed'],mode='lines',line=dict(width=2,color=fastf1.plotting.get_driver_color(driver_compared,session)), name=driver_compared),row=2,col=1)
fig.add_trace(go.Scatter(x=telemetry_data[reference_driver]['Distance'], y=telemetry_data[reference_driver]['Speed'],mode='lines',line=dict(width=2,color=fastf1.plotting.get_driver_color(reference_driver,session)), name=reference_driver),row=2,col=1)
fig.add_trace(go.Scatter(x=telemetry_data[driver_compared]['Distance'], y=telemetry_data[driver_compared]['Throttle'],mode='lines',line=dict(width=2,color=fastf1.plotting.get_driver_color(driver_compared,session)), name=driver_compared, showlegend=False),row=3,col=1)
fig.add_trace(go.Scatter(x=telemetry_data[reference_driver]['Distance'], y=telemetry_data[reference_driver]['Throttle'],mode='lines',line=dict(width=2,color=fastf1.plotting.get_driver_color(reference_driver,session)), name=reference_driver, showlegend=False),row=3,col=1)
fig.add_trace(go.Scatter(x=telemetry_data[driver_compared]['Distance'], y=telemetry_data[driver_compared]['Brake'],mode='lines',line=dict(width=2,color=fastf1.plotting.get_driver_color(driver_compared,session)), name=driver_compared, showlegend=False),row=4,col=1)
fig.add_trace(go.Scatter(x=telemetry_data[reference_driver]['Distance'], y= telemetry_data[reference_driver]['Brake'],mode='lines',line=dict(width=2,color=fastf1.plotting.get_driver_color(reference_driver,session)), name=reference_driver, showlegend=False),row=4,col=1)

circuit_info = session.get_circuit_info()

for _, corner in circuit_info.corners.iterrows():       # type: ignore

    fig.add_vline(
        x=corner['Distance'],
        line_width=1,
        line_dash='dot',
        line_color="#5c5c5c"
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
    title=f'Comparison of Lap {lap_number} - {SESSION_NAME} {YEAR}',
    legend=dict(x=1.02, y=1.0),
    margin=dict(l=.3,r=180, t=50, b=0),
    template='plotly_dark',
    paper_bgcolor="#1d1d1d",   # Outer margin color
    plot_bgcolor='#2b2b2b',    # Main graph background color
    xaxis=dict(showgrid=True, gridcolor="#5c5c5c", zerolinecolor="#5c5c5c"),
    yaxis=dict(showgrid=True, gridcolor='#5c5c5c', zerolinecolor='#5c5c5c'),


)

fig.update_yaxes(
    title_text="Delta (s)",
    row=1,
    col=1
)

fig.update_yaxes(
    title_text="Speed (km/h)",
    row=2,
    col=1
)

fig.update_yaxes(
    title_text="Throttle (%)",
    range=[0, 100],
    row=3,
    col=1
)

fig.update_yaxes(
    title_text="Brake (On/Off)",
    tickvals=[0, 1],
    ticktext=["Off", "On"],
    range=[-0.1, 1.1],
    row=4,
    col=1
)

fig.update_xaxes(
    title_text="Distance (m)",
    showgrid = True,
    row = 4,
    col = 1
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

fig.add_annotation(x=1.1, y=0.8, xref='paper', yref='paper', text=f"LAP TIMES:", showarrow=False, font=dict(size=12, color="#C35DFF"))
for idx, driver in enumerate(telemetry_data):
    fig.add_annotation(x=1.1, y=.754-(idx * .046),xref='paper', yref = 'paper', text = f"{driver}: {format_time(lap_data[driver]['LapTime'])}",showarrow=False, font = dict(color=fastf1.plotting.get_driver_color(driver, session),size=12))

fig.update_annotations(font_size=12)


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

fig.add_annotation(x=1.15, y=0.6, xref='paper', yref='paper', text=f"LARGEST LOSS({driver_compared}):<br>{largest_losses[0][0]}<br>{largest_losses[0][1]:+.3f}s", showarrow=False, font=dict(color=fastf1.plotting.get_driver_color(driver_compared, session), size=12))
fig.add_annotation(x=1.15, y=0.5, xref='paper', yref='paper', text=f"LARGEST GAIN({driver_compared}):<br>{largest_gains[0][0]}<br>{largest_gains[0][1]:+.3f}s", showarrow=False, font=dict(size=12, color=fastf1.plotting.get_driver_color(driver_compared, session)))


fig.show()
