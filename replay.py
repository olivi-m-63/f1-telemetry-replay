import fastf1
import fastf1.plotting
import plotly.graph_objects as go
import pandas as pd
import numpy as np

fastf1.Cache.enable_cache(r'c:\\Users\\olivi\\python\\fastf1.cache') #replace with your desired cache directory
#change these to set the year, session name, and session type
YEAR = 2026
SESSION_NAME = 'Australian Grand Prix'
SESSION_TYPE = 'R'

lap_number = 11     #set the lap number to analyze for the session

session = fastf1.get_session(YEAR, SESSION_NAME, SESSION_TYPE)
session.load()


def get_driver_telemetry(session, driver, lap_number):       #get telemetry for a specific driver and lap number
    laps = session.laps.pick_driver(driver)
    if len(laps) < (lap_number):
        return None,None
    lap = laps.iloc[lap_number-1]
    telemetry = lap.get_telemetry()
    telemetry['TimeSeconds'] = telemetry['Time'].dt.total_seconds()
    return telemetry, lap       #return telemetry and lap data for the specified driver and lap number, or None if the driver doesn't have enough laps

drivers = session.laps['Driver'].unique()
telemetry_data = {}     #initialize dictionaries to store telemetry and lap data for each driver
lap_data = {}
for driver in drivers:      #store telemetry and lap data in dictionaries
    telemetry, lap = get_driver_telemetry(session, driver, lap_number)
    if telemetry is None:       #if the driver doesn't have enough laps, skip to the next driver
        continue
    telemetry_data[driver] = telemetry
    lap_data[driver] = lap

first_driver = list(telemetry_data.keys())[0]      #add track outline and finish line as the first two traces
traces = [go.Scatter(x=telemetry_data[first_driver]['X'], y=telemetry_data[first_driver]['Y'],mode='lines',line=dict(width=5), name='albert park'),
          go.Scatter(x=[telemetry_data[first_driver]['X'].iloc[0]], y=[telemetry_data[first_driver]['Y'].iloc[0]],mode='markers',marker=dict(size=20, color='white', symbol='star'),name='finish line'),]

max_time = max(     #find the maximum time across all drivers to set the timeline for animation
    telemetry_data[driver]['TimeSeconds'].max() for driver in telemetry_data
)

timeline = np.arange(0, max_time + 0.1, 0.1)      #create a timeline from 0 to max_time with 0.1 second intervals for interpolation

interpolated = {}       #interpolate X and Y positions for each driver at each point in the timeline
for driver, telemetry in telemetry_data.items():
    interpolated[driver] = {
    'X': np.interp(
        timeline,
        telemetry['TimeSeconds'],
        telemetry['X']
    ),
    'Y': np.interp(
        timeline,
        telemetry['TimeSeconds'],
        telemetry['Y']
    ),
    'Distance': np.interp(
        timeline,
        telemetry['TimeSeconds'],
        telemetry['Distance']
    )
}


for driver in telemetry_data:       #add traces for each driver with color based on speed and a marker for the current position, initially set to legendonly
    color = fastf1.plotting.get_driver_color(driver,session)
    traces.append(go.Scatter(x=telemetry_data[driver]['X'], y=telemetry_data[driver]['Y'],mode='markers',marker=dict(color=telemetry_data[driver]['Speed'],colorscale='RdYlGn',showscale=True), name=f"{driver} Speed Map", visible='legendonly'))
    traces.append(go.Scatter(x=[telemetry_data[driver]['X'].iloc[0]], y=[telemetry_data[driver]['Y'].iloc[0]], mode='markers+text', marker=dict(size=15, color=color), name=driver,text=driver, textposition='top center'))
fig = go.Figure(data=traces)

fig.frames = [
    go.Frame(data=[
        go.Scatter(x=[interpolated[driver]['X'][i]], y=[interpolated[driver]['Y'][i]], mode='markers+text', marker=dict(size=15, color=(fastf1.plotting.get_driver_color(driver,session))),text=driver, textposition='top center') for driver in telemetry_data],
        traces=list(range(3, 3 + len(drivers) * 2, 2)))     #update the positions of the driver markers at each point in the timeline, keeping the track outline and finish line traces unchanged
    for i in range(len(timeline))
]

fig.update_layout(
    updatemenus=[dict(type="buttons",
                      buttons=[dict(label="Play",
                                    method="animate",
                                    args=[None])])],
    title=f"{SESSION_NAME} " + str(YEAR) + f" Lap {lap_number}",
    coloraxis_colorbar=dict(x=1.15),
    legend=dict(x=1.1, y=1.0),
    margin=dict(l=0,r=500, t=50, b=0)
)

fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
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
    fig.add_annotation(x=1.6, y=1-(idx * .046),xref='paper', yref = 'paper', text = f"{driver} LAP TIME: {format_time(lap_data[driver]['LapTime'])}",showarrow=False, font = dict(color=fastf1.plotting.get_driver_color(driver, session),size=14))
fig.show()