import fastf1
import fastf1.plotting
import plotly.graph_objects as go
import pandas as pd
fastf1.Cache.enable_cache(r'c:\\Users\\olivi\\python\\fastf1.cache')
#change these to set the year, session name, and session type
YEAR = 2026
SESSION_NAME = 'Australian Grand Prix'
SESSION_TYPE = 'R'
METRIC = 'Brake'     #set the metric to compare, e.g. 'Speed', 'Throttle', 'Brake', etc.
lap_number = 11     #set the lap number to analyze for the session
drivers_to_compare = ['RUS', 'VER']     #set the drivers to compare by their three-letter codes, e.g. 'HAM' for Lewis Hamilton, 'VER' for Max Verstappen, etc.

session = fastf1.get_session(YEAR, SESSION_NAME, SESSION_TYPE)
session.load()




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



traces = []

for driver in telemetry_data:       #add traces for each driver with color based on speed and a marker for the current position, initially set to legendonly
    color = fastf1.plotting.get_driver_color(driver,session)
    traces.append(go.Scatter(x=telemetry_data[driver]['Distance'], y=telemetry_data[driver][METRIC],mode='lines',line=dict(width=2,color=color), name=driver, visible='legendonly'))



fig = go.Figure(data=traces)

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
    title=f'{METRIC} Comparison of Lap {lap_number} - {SESSION_NAME} {YEAR}',
    legend=dict(x=1.1, y=1.0),
    margin=dict(l=.3,r=300, t=50, b=0),
    template='ggplot2'

)

UNITS = {
    "Speed": "km/h",
    "Throttle": "%",
    "Brake": "On/Off",
    "RPM": "rpm",
    "nGear": "gear"
}

fig.update_yaxes(
    title_text=f'{METRIC} ({UNITS.get(METRIC, "")})',
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


for idx, driver in enumerate(telemetry_data):
    fig.add_annotation(x=1.27, y=.8-(idx * .046),xref='paper', yref = 'paper', text = f"{driver} LAP TIME: {format_time(lap_data[driver]['LapTime'])}",showarrow=False, font = dict(color=fastf1.plotting.get_driver_color(driver, session),size=14))

fig.show()