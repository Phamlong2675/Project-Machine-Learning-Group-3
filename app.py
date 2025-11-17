import pandas as pd
import plotly.graph_objects as go
import gradio as gr
from datetime import timedelta
import numpy as np
from datetime import datetime

def load_daily_data():
    """Loads test_data.xlsx (used for the Daily Forecast tab)."""
    try:
        test_data = pd.read_excel('data/processed/test_data.xlsx')
        test_data['datetime'] = pd.to_datetime(test_data['datetime'])
        print("SUCCESS: Loaded 'test_data.xlsx' for Daily Forecast.")
        return test_data
    except FileNotFoundError:
        print("WARNING: test_data.xlsx not found. Using dummy daily data.")
        daily_index = pd.date_range('2025-10-01', periods=10, freq='D')
        temps = np.random.uniform(25, 30, size=len(daily_index))
        humidity = np.random.uniform(60, 90, size=len(daily_index))
        wind_speed_dummy = np.random.uniform(5, 20, size=len(daily_index)) 
        test_data = pd.DataFrame({
            'datetime': daily_index, 
            'temp': temps,
            'humidity': humidity,
            'windspeed': wind_speed_dummy
        })
        return test_data

def load_hourly_data():
    """Loads test_data_h.xlsx (used for the Hourly Forecast tab)."""
    try:
        test_data_h = pd.read_excel('data/processed/test_data_h.xlsx')
        test_data_h['datetime'] = pd.to_datetime(test_data_h['datetime'])
        print("SUCCESS: Loaded 'test_data_h.xlsx' for Hourly Forecast.")
        return test_data_h
    except FileNotFoundError:
        print("WARNING: test_data_h.xlsx not found. Using dummy hourly data.")
        hourly_index = pd.date_range('2025-10-01 00:00', periods=24, freq='H')
        temps_h = np.random.uniform(25, 30, size=len(hourly_index))
        test_data_h = pd.DataFrame({'datetime': hourly_index, 'temp': temps_h})
        return test_data_h

def preload_historical_data():
    """
    (This function runs only once on startup)
    Loads and concatenates 3 files (train, val, test) for the Historical Analysis tab.
    """
    try:
        base_path = 'data/processed/'
        train_file = base_path + 'train_data.xlsx'
        val_file = base_path + 'val_data.xlsx'
        test_file = base_path + 'test_data.xlsx'
        
        train_df = pd.read_excel(train_file)
        val_df = pd.read_excel(val_file)
        test_df = pd.read_excel(test_file)
        
        all_data = pd.concat([train_df, val_df, test_df], ignore_index=True)
        all_data['datetime'] = pd.to_datetime(all_data['datetime'])
        
        required_cols = ['datetime', 'temp', 'humidity', 'windspeed'] 
        if not all(col in all_data.columns for col in required_cols):
            print(f"ERROR: Concatenated data (train, val, test) is missing columns. Required: {required_cols}")
            raise FileNotFoundError("Concatenated data is missing columns.")
            
        print(f"SUCCESS: Loaded and concatenated 3 files (train, val, test) into memory.")
        # Sort to find min/max dates correctly
        all_data = all_data.sort_values(by='datetime')
        return all_data

    except FileNotFoundError as e:
        print(f"WARNING: Could not find files (Error: {e}). Using dummy historical data.")
        
        days = pd.date_range('2024-01-01', periods=700, freq='D')
        temps = np.random.uniform(15, 35, size=len(days)) + np.sin(np.arange(len(days)) * 0.02) * 5
        humidity = np.random.uniform(60, 90, size=len(days))
        wind_speed_dummy = np.random.uniform(5, 20, size=len(days))
        
        full_data = pd.DataFrame({
            'datetime': days, 
            'temp': temps, 
            'humidity': humidity, 
            'windspeed': wind_speed_dummy
        })
        return full_data

# --- Load historical data ONCE on startup ---
GLOBAL_HISTORY_DATA = preload_historical_data()

# --- Get min/max dates from the preloaded data ---
DEFAULT_START_DATE = GLOBAL_HISTORY_DATA['datetime'].min().strftime("%Y-%m-%d")
DEFAULT_END_DATE = GLOBAL_HISTORY_DATA['datetime'].max().strftime("%Y-%m-%d")


# --- FUNCTION 3 (MAIN): Return preloaded data ---
def load_full_history_data():
    """
    (This function is called by Tab 1)
    Returns the globally preloaded historical data.
    """
    print("INFO: Returning GLOBAL_HISTORY_DATA from memory.")
    return GLOBAL_HISTORY_DATA


# --- Weather icon helper ---
def get_weather_icon(temp):
    if temp >= 28:
        return "☀️"    # Hot
    elif temp >= 24:
        return "🌤️"  # Warm
    elif temp >= 20:
        return "⛅"    # Mild
    else:
        return "❄️"    # Cold

# --- Daily forecast (Uses load_daily_data) ---
def create_daily_forecast():
    # Load its specific data
    test_data = load_daily_data()
    
    history_days = 10
    # Get the last 10 days from *test_data* as history
    history_df = test_data[['datetime','temp']].copy().sort_values(by='datetime').tail(history_days)
    history_df = history_df.rename(columns={'temp':'temperature'})
    history_df['icon'] = history_df['temperature'].apply(get_weather_icon)

    # Forecast data (hardcoded)
    future_dates = pd.to_datetime(['2025-10-02','2025-10-03','2025-10-04','2025-10-05','2025-10-06'])
    future_temps = [27.98, 28.94, 28.05, 28.13, 28.30]
    lower_temps = [26.44, 27.40, 26.51, 26.60, 26.77]
    upper_temps = [29.51, 30.47, 29.58, 29.67, 29.84]
    future_df = pd.DataFrame({
        'datetime': future_dates,
        'temperature': future_temps,
        'lower': lower_temps,
        'upper': upper_temps
    })
    future_df['icon'] = future_df['temperature'].apply(get_weather_icon)

    combined_df = pd.concat([history_df, future_df], ignore_index=True)

    # --- Plotly chart ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df['datetime'],
        y=history_df['temperature'],
        mode='lines+markers',
        name='History',
        line=dict(color='#FFC966', width=3, shape='spline', smoothing=1.3),
        marker=dict(color='#FFC966', size=8),
        hovertemplate='%{y:.1f}°C<extra></extra>'
    ))
    connect_df = pd.DataFrame({
        'datetime':[history_df['datetime'].iloc[-1], future_df['datetime'].iloc[0]],
        'temperature':[history_df['temperature'].iloc[-1], future_df['temperature'].iloc[0]]
    })
    fig.add_trace(go.Scatter(
        x=connect_df['datetime'],
        y=connect_df['temperature'],
        mode='lines',
        line=dict(color='#FFC966', width=3, shape='spline', smoothing=1.3),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=future_df['datetime'],
        y=future_df['temperature'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#FFAA00', width=3, shape='spline', smoothing=1.3),
        marker=dict(color='#FFAA00', size=8),
        hovertemplate='%{y:.1f}°C<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=future_df['datetime'],
        y=future_df['lower'],
        mode='lines',
        name='Lower Bound',
        line=dict(color='#FF9999', width=2, dash='dash', shape='spline', smoothing=1.3),
        hovertemplate='Lower Bound: %{y:.1f}°C<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=future_df['datetime'],
        y=future_df['upper'],
        mode='lines',
        name='Upper Bound',
        line=dict(color='#FF3300', width=2, dash='dash', shape='spline', smoothing=1.3),
        hovertemplate='Upper Bound: %{y:.1f}°C<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=combined_df['datetime'],
        y=combined_df['temperature'] + 0.3,
        mode='text',
        text=[f"{t:.1f}°C" for t in combined_df['temperature']],
        textposition='top center',
        textfont=dict(size=15, color='black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=combined_df['datetime'],
        y=combined_df['temperature'] - 0.3,
        mode='text',
        text=combined_df['icon'],
        textposition='bottom center',
        textfont=dict(size=15),
        showlegend=False,
        hoverinfo='skip'
    ))
    min_val_icon = (combined_df['temperature'] - 0.3).min() 
    min_val_lower = future_df['lower'].min()
    min_y = min(min_val_icon, min_val_lower)
    max_val_text = (combined_df['temperature'] + 0.3).max()
    max_val_upper = future_df['upper'].max()
    max_y = max(max_val_text, max_val_upper)
    y_padding = 0.5
    fig.update_layout(
        title=dict(text="<b>Temperature Daily Forecast Chart</b>", x=0.5),
        hovermode='x unified',
        plot_bgcolor='#D6EAF8', paper_bgcolor='#D6EAF8',
        xaxis=dict(title=None, showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(
            title=None, 
            showticklabels=False, 
            showgrid=False, 
            zeroline=False,
            range=[min_y - y_padding, max_y + y_padding]
        )
    )
    
    # --- HTML cards ---
    html_output = "<div style='display: flex; overflow-x: auto; gap: 10px; padding: 10px;'>"
    DAYS_EN = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    for i in range(len(combined_df)):
        date = combined_df.iloc[i]['datetime']
        temp = combined_df.iloc[i]['temperature']
        day_of_week = DAYS_EN[date.weekday()]
        day_str = date.strftime('%d-%m')
        icon = combined_df.iloc[i]['icon']
        color_bg = '#ffffff' if i < len(history_df) else '#fff8dc'
        
        style_overrides = ""
        # Check if this is the last item of history_df
        if i == len(history_df) - 1:
            # Scale up and add red border
            style_overrides = "border: 3px solid #E74C3C; transform: scale(1.12); z-index: 10; box-shadow: 0 6px 12px rgba(0,0,0,0.15);"
        else:
            style_overrides = "border: 1px solid #ddd; box-shadow: 0 4px 8px rgba(0,0,0,0.05);"
        
        html_output += f"""
        <div style='border-radius:12px; padding:20px; min-width:130px; 
                       text-align:center; background-color:{color_bg}; 
                       {style_overrides}'> 
            <h3 style='margin:0; font-size:1em; color:#0056b3;'>{day_of_week}</h3>
            <p style='font-size:0.9em; margin:5px 0; color:#555;'>{day_str}</p>
            <p style='font-size:2em; margin:10px 0;'>{icon}</p>
            <p style='font-size:1.5em; font-weight:bold; color:#0056b3; margin:5px 0;'>{temp:.1f}°C</p>
        </div>
        """
    html_output += "</div>"
    return fig, html_output

# --- Hourly forecast (Uses load_hourly_data) ---
def create_hourly_forecast():
    # Load its specific data
    test_data_h = load_hourly_data()

    history_hours = 12
    # Get the last 12 hours from *test_data_h* as history
    history_df = test_data_h[['datetime','temp']].copy().sort_values(by='datetime').tail(history_hours)
    history_df = history_df.rename(columns={'temp':'temperature'})
    history_df['icon'] = history_df['temperature'].apply(get_weather_icon)

    # Forecast data (hardcoded)
    future_dates = [history_df['datetime'].max() + pd.Timedelta(hours=i+1) for i in range(3)]
    future_temps = [26.68, 26.53, 26.15]
    lower_temps = [26.02, 25.87, 25.49]
    upper_temps = [27.33, 27.18, 26.80]
    future_df = pd.DataFrame({
        'datetime': future_dates,
        'temperature': future_temps,
        'lower': lower_temps,
        'upper': upper_temps
    })
    future_df['icon'] = future_df['temperature'].apply(get_weather_icon)

    combined_df = pd.concat([history_df, future_df], ignore_index=True)

    # --- Plotly chart ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df['datetime'],
        y=history_df['temperature'],
        mode='lines+markers',
        name='History',
        line=dict(color='#FFC966', width=3, shape='spline', smoothing=1.3),
        marker=dict(color='#FFC966', size=8),
        hovertemplate='%{y:.1f}°C<extra></extra>'
    ))
    connect_df = pd.DataFrame({
        'datetime':[history_df['datetime'].iloc[-1], future_df['datetime'].iloc[0]],
        'temperature':[history_df['temperature'].iloc[-1], future_df['temperature'].iloc[0]]
    })
    fig.add_trace(go.Scatter(
        x=connect_df['datetime'],
        y=connect_df['temperature'],
        mode='lines',
        line=dict(color='#FFC966', width=3, shape='spline', smoothing=1.3),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=future_df['datetime'],
        y=future_df['temperature'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#FFAA00', width=3, shape='spline', smoothing=1.3),
        marker=dict(color='#FFAA00', size=8),
        hovertemplate='%{y:.1f}°C<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=future_df['datetime'], y=future_df['lower'],
        mode='lines', name='Lower Bound',
        line=dict(color='#FF9999', width=2, dash='dash', shape='spline', smoothing=1.3),
        hovertemplate='Lower Bound: %{y:.1f}°C<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=future_df['datetime'], y=future_df['upper'],
        mode='lines', name='Upper Bound',
        line=dict(color='#FF3300', width=2, dash='dash', shape='spline', smoothing=1.3),
        hovertemplate='Upper Bound: %{y:.1f}°C<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=combined_df['datetime'],
        y=combined_df['temperature'] + 0.15,
        mode='text',
        text=[f"{t:.1f}°C" for t in combined_df['temperature']],
        textposition='top center',
        textfont=dict(size=15, color='black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=combined_df['datetime'],
        y=combined_df['temperature'] - 0.2,
        mode='text',
        text=combined_df['icon'],
        textposition='bottom center',
        textfont=dict(size=15),
        showlegend=False,
        hoverinfo='skip'
    ))
    min_val_icon = (combined_df['temperature'] - 0.2).min()
    min_val_lower = future_df['lower'].min()
    min_y = min(min_val_icon, min_val_lower)
    max_val_text = (combined_df['temperature'] + 0.15).max()
    max_val_upper = future_df['upper'].max()
    max_y = max(max_val_text, max_val_upper)
    y_padding = 0.2
    fig.update_layout(
        title=dict(text="<b>Temperature Hourly Forecast Chart</b>", x=0.5),
        hovermode='x unified',
        plot_bgcolor='#D6EAF8', paper_bgcolor='#D6EAF8',
        xaxis=dict(title=None, showticklabels=False, showgrid=False, zeroline=False), 
        yaxis=dict(
            title=None, 
            showticklabels=False, 
            showgrid=False, 
            zeroline=False,
            range=[min_y - y_padding, max_y + y_padding]
        )
    )
    
    # --- HTML cards ---
    html_output = "<div style='display: flex; overflow-x: auto; gap: 10px; padding: 10px;'>"
    for i in range(len(combined_df)):
        dt = combined_df.iloc[i]['datetime']
        temp = combined_df.iloc[i]['temperature']
        icon = combined_df.iloc[i]['icon']
        time_str = dt.strftime('%d-%m %H:%M')
        color_bg = '#ffffff' if i < len(history_df) else '#fff8dc'
        
        style_overrides = ""
        # Check if this is the last item of history_df
        if i == len(history_df) - 1:
            # Scale up and add red border
            style_overrides = "border: 3px solid #E74C3C; transform: scale(1.12); z-index: 10; box-shadow: 0 6px 12px rgba(0,0,0,0.15);"
        else:
            style_overrides = "border: 1px solid #ddd; box-shadow: 0 4px 8px rgba(0,0,0,0.05);"
            
        html_output += f"""
        <div style='border-radius:12px; padding:20px; min-width:130px; 
                       text-align:center; background-color:{color_bg}; 
                       {style_overrides}'>
            <p style='margin:0; font-size:0.9em; color:#555;'>{time_str}</p>
            <p style='font-size:2em; margin:10px 0;'>{icon}</p>
            <p style='font-size:1.5em; font-weight:bold; color:#0056b3; margin:5px 0;'>{temp:.1f}°C</p>
        </div>
        """
    html_output += "</div>"
    return fig, html_output


# --- Handler function for the historical tab (Uses load_full_history_data) ---
def analyze_history(start_date, end_date):
    """Filters data, calculates stats, and draws the plot for the historical tab."""
    
    # 1. Validate input (Textbox can be empty)
    if not start_date or not end_date:
        return go.Figure().update_layout(title="Please enter a start and end date"), "<p style='color:red; text-align:center;'>Please enter both a start and end date (YYYY-MM-DD).</p>"
    
    try:
        # Convert text input to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
    except Exception as e:
        return go.Figure().update_layout(title="Invalid Date Format"), f"<p style='color:red; text-align:center;'>Invalid date format. Please use YYYY-MM-DD. Error: {e}</p>"

    
    if start_dt > end_dt:
        return go.Figure().update_layout(title="Date Error"), "<p style='color:red; text-align:center;'>Start date cannot be after the end date.</p>"

    # 2. Load and filter data (Get from preloaded GLOBAL variable)
    all_data = load_full_history_data()
    mask = (all_data['datetime'] >= start_dt) & (all_data['datetime'] <= end_dt)
    df = all_data[mask]
    
    if df.empty:
        return go.Figure().update_layout(title="No Data"), f"<p style='text-align:center;'>No data found for the selected range: {start_date} to {end_date}.</p>"
    
    # 3. Calculate average stats (using 'windspeed')
    avg_temp = df['temp'].mean()
    avg_humidity = df['humidity'].mean()
    avg_wind = df['windspeed'].mean() 
    
    # 4. Create HTML output for stats
    stats_html = f"""
    <div style='display: flex; gap: 20px; justify-content: space-around; text-align: center; padding: 10px;'>
        <div style='background-color: #e0f0ff; padding: 15px; border-radius: 10px; flex-grow: 1;'>
            <h3 style='margin: 0; color: #0056b3; font-size: 1.1em;'>Avg. Temp</h3>
            <p style='font-size: 2em; font-weight: bold; margin: 5px 0; color: #0056b3;'>{avg_temp:.1f}°C</p>
        </div>
        <div style='background-color: #e0fff0; padding: 15px; border-radius: 10px; flex-grow: 1;'>
            <h3 style='margin: 0; color: #006b56; font-size: 1.1em;'>Avg. Humidity</h3>
            <p style='font-size: 2em; font-weight: bold; margin: 5px 0; color: #006b56;'>{avg_humidity:.1f}%</p>
        </div>
        <div style='background-color: #fff0e0; padding: 15px; border-radius: 10px; flex-grow: 1;'>
            <h3 style='margin: 0; color: #6b4000; font-size: 1.1em;'>Avg. Wind Speed</h3>
            <p style='font-size: 2em; font-weight: bold; margin: 5px 0; color: #6b4000;'>{avg_wind:.1f} km/h</p>
        </div>
    </div>
    """
    
    # 5. Create Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['temp'],
        mode='lines+markers',
        name='Actual Temperature',
        line=dict(color='#0056b3', width=2, shape='spline'),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>Actual Temperature from {start_date} to {end_date}</b>", x=0.5),
        plot_bgcolor='#D6EAF8', 
        paper_bgcolor='#D6EAF8',
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title="Temperature (°C)"
    )
            
    return fig, stats_html


# --- Load all forecasts (Calls functions for the two forecast tabs) ---
def load_all_forecasts():
    """This function calls the creation functions for the FORECAST tabs."""
    fig_daily, html_daily = create_daily_forecast()
    fig_hourly, html_hourly = create_hourly_forecast()
    return fig_daily, html_daily, fig_hourly, html_hourly

# --- Gradio interface CSS ---
css_code = """
.gradio-container {
    background-image: url('https://raw.githubusercontent.com/tungvoi38/Machine_Learning_Group_3/main/temperature_prediction_Hanoi/notebooks/cloud.png') !important;
    background-size: cover !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}
.gr-block, .gr-panel, .gr-box {
    background: rgba(255,255,255,0.75) !important;
    backdrop-filter: blur(4px);
    border-radius: 12px !important;
}
.footer { text-align:center; color:white; font-size:16px; padding:10px; }

/* CSS for the date Textbox (using class) */
.custom-date-box input {
    background-color: #f0f8ff !important;
    border: 2px solid #0056b3 !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    font-weight: 500;
    text-align: center;
    color: #0056b3;
}
.custom-date-box input:focus {
    border-color: #FFAA00 !important;
    box-shadow: 0 0 8px rgba(255,170,0,0.5) !important;
}

/* --- CSS TO CENTER AND ENLARGE TABS --- */
/* 1. Center the tab bar */
div[role="tablist"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
    gap: 10px !important;
    padding-top: 10px !important;
}
/* 2. Enlarge the TAB BUTTONS */
div[role="tablist"] button {
    font-size: 18px !important;
    padding: 15px 30px !important;
    font-weight: 600 !important;
    border-radius: 10px 10px 0 0 !important;
    flex-grow: 0 !important;
    min-width: 220px !important;
    background-color: #e0f0ff !important; 
    color: #0056b3 !important;      
    border: 2px solid #0056b3 !important; 
    border-bottom: none !important;
}
/* 3. Style for the SELECTED tab */
div[role="tablist"] button[aria-selected="true"] {
    background-color: #0056b3 !important;
    color: white !important;
}
"""

with gr.Blocks(css=css_code) as iface:
    gr.Markdown("<h1 style='text-align:center;color:white;font-size:42px;'>🌦️ Hanoi Temperature Forecast App</h1>")
    gr.Markdown("---")
    
    with gr.Tabs():
        # --- TAB 1 (Historical) ---
        with gr.Tab(label="📈 Historical Analysis"):
            with gr.Column():
                gr.Markdown("<h2 style='color:white;font-size:28px;'>📈 Historical Data Analysis</h2>")
                
                with gr.Row():
                    start_date_input = gr.Textbox(
                        label="Start Date", 
                        value=DEFAULT_START_DATE,
                        placeholder="YYYY-MM-DD", 
                        elem_classes=["custom-date-box"]
                    )
                    end_date_input = gr.Textbox(
                        label="End Date", 
                        value=DEFAULT_END_DATE,
                        placeholder="YYYY-MM-DD", 
                        elem_classes=["custom-date-box"]
                    )
                
                submit_btn = gr.Button("Analyze Data", variant="primary")
                
                gr.Markdown("<h3 style='color:white; font-weight:bold; text-align:center; margin-top: 20px;'>Key Statistics</h3>")
                history_stats_output = gr.HTML()
                
                gr.Markdown("<h3 style='color:white; font-weight:bold; text-align:center; margin-top: 20px;'>Temperature Trend</h3>")
                history_plot_output = gr.Plot()
        
        # --- TAB 2 (Daily Forecast) ---
        with gr.Tab(label="📅 Daily Forecast"):
            with gr.Column(): 
                gr.Markdown("<h2 style='color:white;font-size:28px;'>📅 5-Day Daily Forecast</h2>")
                daily_cards_output = gr.HTML()
                daily_plot_output = gr.Plot()
                
        # --- TAB 3 (Hourly Forecast) ---
        with gr.Tab(label="🕒 Hourly Forecast"):
            with gr.Column():
                gr.Markdown("<h2 style='color:white;font-size:28px;'>🕒 3-Hour Hourly Forecast</h2>")
                hourly_cards_output = gr.HTML()
                hourly_plot_output = gr.Plot()

    gr.Markdown("---")
    gr.Markdown("© 2025 - Machine Learning Project: Hanoi Temperature Forecasting - Group 3 - DSEB 65B", elem_classes=["footer"])

    # --- EVENT HANDLERS ---
    
    # 1. Page load event (for forecast tabs)
    iface.load(
        fn=load_all_forecasts, 
        inputs=None, 
        outputs=[daily_plot_output, daily_cards_output, hourly_plot_output, hourly_cards_output]
    )
    
    # 2. Button click event (for historical tab)
    submit_btn.click(
        fn=analyze_history,
        inputs=[start_date_input, end_date_input],
        outputs=[history_plot_output, history_stats_output]
    )

if __name__ == "__main__":
    iface.launch()