from flask import Flask, render_template, jsonify
import pandas as pd
import os
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "output", "reports")

def load_data(filename):
    filepath = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame()

@app.route('/')
def index():
    # Load Summary Data
    status_df = load_data("status_distribution.csv")
    daily_df = load_data("daily_traffic.csv")
    suspicious_df = load_data("suspicious_ips.csv")
    
    total_requests = daily_df['total_requests'].sum() if not daily_df.empty else 0
    total_errors = daily_df['errors'].sum() if not daily_df.empty else 0
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
    suspicious_count = len(suspicious_df) if not suspicious_df.empty else 0
    
    summary = {
        "total_requests": f"{total_requests:,}",
        "total_errors": f"{total_errors:,}",
        "error_rate": f"{error_rate:.2f}%",
        "suspicious_ips": f"{suspicious_count:,}"
    }

    # 1. Traffic Over Time (Daily)
    fig_daily = go.Figure()
    if not daily_df.empty:
        # Sort chronologically
        daily_df['date'] = pd.to_datetime(daily_df['day'], format='%d/%b/%Y')
        daily_df = daily_df.sort_values('date')
        
        fig_daily.add_trace(go.Scatter(x=daily_df['day'].tolist(), y=daily_df['total_requests'].tolist(),
                                     mode='lines+markers', name='Total Requests',
                                     line=dict(color='#3b82f6', width=3)))
        fig_daily.add_trace(go.Scatter(x=daily_df['day'].tolist(), y=daily_df['errors'].tolist(),
                                     mode='lines+markers', name='Errors',
                                     line=dict(color='#ef4444', width=2)))
        fig_daily.update_layout(title="Daily Traffic & Error Trends",
                              xaxis_title="Date", yaxis_title="Count",
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='#e2e8f0'), margin=dict(l=0, r=0, t=40, b=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    graph_daily = json.dumps(fig_daily, cls=plotly.utils.PlotlyJSONEncoder)

    # 2. Status Code Distribution
    fig_status = go.Figure()
    if not status_df.empty:
        status_df['status'] = status_df['status'].astype(str)
        # Create categories for colors
        color_map = {}
        for status in status_df['status']:
            if status.startswith('2'): color_map[status] = '#22c55e' # Green
            elif status.startswith('3'): color_map[status] = '#eab308' # Yellow
            elif status.startswith('4'): color_map[status] = '#f97316' # Orange
            elif status.startswith('5'): color_map[status] = '#ef4444' # Red
            else: color_map[status] = '#94a3b8' # Gray
            
        fig_status.add_trace(go.Pie(labels=status_df['status'].tolist(), values=status_df['count'].tolist(),
                                    hole=0.4, marker=dict(colors=[color_map.get(s, '#94a3b8') for s in status_df['status'].tolist()])))
        fig_status.update_layout(title="HTTP Status Codes",
                               plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='#e2e8f0'), margin=dict(l=0, r=0, t=40, b=0))
    graph_status = json.dumps(fig_status, cls=plotly.utils.PlotlyJSONEncoder)

    # 3. Top Endpoints
    top_ep_df = load_data("top_endpoints.csv")
    fig_ep = go.Figure()
    if not top_ep_df.empty:
        # Limit to top 10 and shorten long URLs for display
        df_ep = top_ep_df.head(10).copy()
        df_ep['short_ep'] = df_ep['endpoint'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
        
        fig_ep.add_trace(go.Bar(x=df_ep['hits'].tolist(), y=df_ep['short_ep'].tolist(), orientation='h',
                                marker=dict(color=df_ep['hits'].tolist(), colorscale='Blues')))
        fig_ep.update_layout(title="Top 10 Most Accessed Endpoints", yaxis={'categoryorder':'total ascending'},
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='#e2e8f0'), margin=dict(l=0, r=0, t=40, b=0),
                           coloraxis_showscale=False)
    graph_ep = json.dumps(fig_ep, cls=plotly.utils.PlotlyJSONEncoder)

    # 4. Hourly Anomaly Detection
    hourly_df = load_data("hourly_traffic.csv")
    fig_hourly = go.Figure()
    if not hourly_df.empty:
        # Combine day and hour and sort chronologically
        hourly_df['datetime'] = pd.to_datetime(hourly_df['day'] + ' ' + hourly_df['hour'].astype(str).str.zfill(2) + ':00', format='%d/%b/%Y %H:%M')
        hourly_df = hourly_df.sort_values('datetime')
        hourly_df['datetime_str'] = hourly_df['datetime'].dt.strftime('%d/%b/%Y %H:%M')
        
        fig_hourly.add_trace(go.Scatter(x=hourly_df['datetime_str'].tolist(), y=hourly_df['request_count'].tolist(),
                                      mode='lines', name='Requests', line=dict(color='#8b5cf6')))
        fig_hourly.add_trace(go.Scatter(x=hourly_df['datetime_str'].tolist(), y=hourly_df['threshold_high'].tolist(),
                                      mode='lines', name='Anomaly Threshold', 
                                      line=dict(color='#ef4444', dash='dash')))
        
        # Mark anomalies
        anomalies = hourly_df[hourly_df['is_anomaly'] == 'HIGH']
        if not anomalies.empty:
            fig_hourly.add_trace(go.Scatter(x=anomalies['datetime_str'].tolist(), y=anomalies['request_count'].tolist(),
                                          mode='markers', name='Anomalies',
                                          marker=dict(color='red', size=8, symbol='x')))
                                          
        fig_hourly.update_layout(title="Hourly Traffic & Anomaly Detection",
                               plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='#e2e8f0'), margin=dict(l=0, r=0, t=40, b=0),
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    graph_hourly = json.dumps(fig_hourly, cls=plotly.utils.PlotlyJSONEncoder)

    # Top IPs table data
    top_ips_df = load_data("top_ips.csv")
    top_ips = top_ips_df.head(10).to_dict(orient='records') if not top_ips_df.empty else []

    return render_template('index.html', 
                          summary=summary,
                          graph_daily=graph_daily,
                          graph_status=graph_status,
                          graph_ep=graph_ep,
                          graph_hourly=graph_hourly,
                          top_ips=top_ips)

if __name__ == '__main__':
    print("="*60)
    print("Starting Smart Log Analyzer Dashboard...")
    print("Open http://127.0.0.1:5000 in your browser.")
    print("="*60)
    app.run(debug=True, port=5000)
