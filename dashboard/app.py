"""
Universal Orlando Wait Time Dashboard

An interactive Streamlit app to explore wait time patterns across
Universal Orlando theme parks.

Run with: streamlit run dashboard/app.py
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# Configuration
# =============================================================================

st.set_page_config(
    page_title="Universal Orlando Wait Times",
    page_icon="🎢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "wait_times.db"

# Day name mapping
DAY_NAMES = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday"
}

# =============================================================================
# Data Loading
# =============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load all data from the SQLite database."""
    if not DB_PATH.exists():
        return None, None, None

    conn = sqlite3.connect(DB_PATH)

    # Load parks
    parks_df = pd.read_sql_query("SELECT * FROM parks", conn)

    # Load rides with park info
    rides_df = pd.read_sql_query("""
        SELECT r.*, p.name as park_name, l.name as land_name
        FROM rides r
        JOIN parks p ON r.park_id = p.id
        LEFT JOIN lands l ON r.land_id = l.id
    """, conn)

    # Load wait times with all related info
    wait_times_df = pd.read_sql_query("""
        SELECT
            wt.*,
            r.name as ride_name,
            p.name as park_name,
            l.name as land_name
        FROM wait_times wt
        JOIN rides r ON wt.ride_id = r.id
        JOIN parks p ON r.park_id = p.id
        LEFT JOIN lands l ON r.land_id = l.id
    """, conn)

    conn.close()

    if len(wait_times_df) > 0:
        wait_times_df['collected_at'] = pd.to_datetime(wait_times_df['collected_at'])
        wait_times_df['date'] = wait_times_df['collected_at'].dt.date
        wait_times_df['day_name'] = wait_times_df['day_of_week'].map(DAY_NAMES)

    return parks_df, rides_df, wait_times_df


# =============================================================================
# Sidebar Filters
# =============================================================================

def render_sidebar(wait_times_df, rides_df):
    """Render sidebar with filters and return filter values."""
    st.sidebar.title("🎢 Filters")

    # Park filter
    parks = sorted(wait_times_df['park_name'].unique())
    selected_parks = st.sidebar.multiselect(
        "Parks",
        options=parks,
        default=parks,
        help="Select one or more parks to analyze"
    )

    # Date range filter
    if len(wait_times_df) > 0:
        min_date = wait_times_df['date'].min()
        max_date = wait_times_df['date'].max()

        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Select date range to analyze"
        )

        # Handle single date selection
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range
    else:
        start_date = end_date = datetime.now().date()

    # Hour range filter
    hour_range = st.sidebar.slider(
        "Hour Range",
        min_value=0,
        max_value=23,
        value=(8, 22),
        help="Filter by hour of day"
    )

    # Ride filter (optional)
    filtered_rides = rides_df[rides_df['park_name'].isin(selected_parks)]
    ride_options = ["All Rides"] + sorted(filtered_rides['name'].unique().tolist())
    selected_ride = st.sidebar.selectbox(
        "Specific Ride (optional)",
        options=ride_options,
        help="Focus on a specific ride"
    )

    # Weekend filter
    day_filter = st.sidebar.radio(
        "Days",
        options=["All Days", "Weekdays Only", "Weekends Only"],
        help="Filter by day type"
    )

    return {
        'parks': selected_parks,
        'start_date': start_date,
        'end_date': end_date,
        'hour_range': hour_range,
        'ride': None if selected_ride == "All Rides" else selected_ride,
        'day_filter': day_filter
    }


def apply_filters(df, filters):
    """Apply sidebar filters to the dataframe."""
    filtered = df.copy()

    # Park filter
    if filters['parks']:
        filtered = filtered[filtered['park_name'].isin(filters['parks'])]

    # Date filter
    filtered = filtered[
        (filtered['date'] >= filters['start_date']) &
        (filtered['date'] <= filters['end_date'])
    ]

    # Hour filter
    filtered = filtered[
        (filtered['hour'] >= filters['hour_range'][0]) &
        (filtered['hour'] <= filters['hour_range'][1])
    ]

    # Ride filter
    if filters['ride']:
        filtered = filtered[filtered['ride_name'] == filters['ride']]

    # Day filter
    if filters['day_filter'] == "Weekdays Only":
        filtered = filtered[filtered['is_weekend'] == 0]
    elif filters['day_filter'] == "Weekends Only":
        filtered = filtered[filtered['is_weekend'] == 1]

    # Only include open rides with valid wait times
    filtered = filtered[(filtered['is_open'] == 1) & (filtered['wait_time'].notna())]

    return filtered


# =============================================================================
# Dashboard Pages
# =============================================================================

def render_overview(df, parks_df, rides_df):
    """Render the overview page with key statistics."""
    st.header("📊 Overview")

    if len(df) == 0:
        st.warning("No data available for the selected filters.")
        return

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", f"{len(df):,}")

    with col2:
        st.metric("Avg Wait Time", f"{df['wait_time'].mean():.0f} min")

    with col3:
        st.metric("Max Wait Time", f"{df['wait_time'].max():.0f} min")

    with col4:
        st.metric("Rides Tracked", f"{df['ride_id'].nunique()}")

    st.divider()

    # Two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        # Average wait by park
        park_avg = df.groupby('park_name')['wait_time'].mean().reset_index()
        park_avg = park_avg.sort_values('wait_time', ascending=True)

        fig = px.bar(
            park_avg,
            x='wait_time',
            y='park_name',
            orientation='h',
            title="Average Wait Time by Park",
            labels={'wait_time': 'Average Wait (min)', 'park_name': ''},
            color='wait_time',
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Wait time distribution
        fig = px.histogram(
            df,
            x='wait_time',
            nbins=30,
            title="Wait Time Distribution",
            labels={'wait_time': 'Wait Time (min)', 'count': 'Frequency'},
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig, use_container_width=True)

    # Top rides table
    st.subheader("🎢 Top 10 Rides by Average Wait")
    top_rides = df.groupby(['ride_name', 'park_name']).agg({
        'wait_time': ['mean', 'max', 'count']
    }).round(0)
    top_rides.columns = ['Avg Wait (min)', 'Max Wait (min)', 'Data Points']
    top_rides = top_rides.sort_values('Avg Wait (min)', ascending=False).head(10)
    st.dataframe(top_rides, use_container_width=True)


def render_hourly_analysis(df):
    """Render hourly wait time analysis."""
    st.header("⏰ Wait Times by Hour")

    if len(df) == 0:
        st.warning("No data available for the selected filters.")
        return

    # Hourly average by park
    hourly = df.groupby(['hour', 'park_name'])['wait_time'].mean().reset_index()

    fig = px.line(
        hourly,
        x='hour',
        y='wait_time',
        color='park_name',
        title="Average Wait Time by Hour of Day",
        labels={'hour': 'Hour', 'wait_time': 'Average Wait (min)', 'park_name': 'Park'},
        markers=True
    )
    fig.update_xaxes(tickmode='linear', tick0=0, dtick=2)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    # Best hours recommendation
    st.subheader("💡 Best Times to Visit")

    best_hours = df.groupby('hour')['wait_time'].mean().sort_values()
    worst_hours = df.groupby('hour')['wait_time'].mean().sort_values(ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"**Shortest waits:** {best_hours.index[0]}:00 - {best_hours.index[0]+1}:00 ({best_hours.iloc[0]:.0f} min avg)")
        if len(best_hours) > 1:
            st.success(f"**Second best:** {best_hours.index[1]}:00 - {best_hours.index[1]+1}:00 ({best_hours.iloc[1]:.0f} min avg)")

    with col2:
        st.error(f"**Longest waits:** {worst_hours.index[0]}:00 - {worst_hours.index[0]+1}:00 ({worst_hours.iloc[0]:.0f} min avg)")
        if len(worst_hours) > 1:
            st.error(f"**Second busiest:** {worst_hours.index[1]}:00 - {worst_hours.index[1]+1}:00 ({worst_hours.iloc[1]:.0f} min avg)")


def render_daily_analysis(df):
    """Render daily wait time analysis."""
    st.header("📅 Wait Times by Day of Week")

    if len(df) == 0:
        st.warning("No data available for the selected filters.")
        return

    # Daily average by park
    daily = df.groupby(['day_of_week', 'day_name', 'park_name'])['wait_time'].mean().reset_index()
    daily = daily.sort_values('day_of_week')

    fig = px.bar(
        daily,
        x='day_name',
        y='wait_time',
        color='park_name',
        barmode='group',
        title="Average Wait Time by Day of Week",
        labels={'day_name': 'Day', 'wait_time': 'Average Wait (min)', 'park_name': 'Park'},
        category_orders={'day_name': list(DAY_NAMES.values())}
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    # Weekend vs weekday comparison
    st.subheader("📊 Weekend vs Weekday")

    weekend_avg = df[df['is_weekend'] == 1]['wait_time'].mean()
    weekday_avg = df[df['is_weekend'] == 0]['wait_time'].mean()

    if pd.notna(weekend_avg) and pd.notna(weekday_avg):
        diff = weekend_avg - weekday_avg
        diff_pct = (diff / weekday_avg) * 100 if weekday_avg > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Weekday Average", f"{weekday_avg:.0f} min")
        with col2:
            st.metric("Weekend Average", f"{weekend_avg:.0f} min")
        with col3:
            st.metric("Difference", f"{diff:+.0f} min", f"{diff_pct:+.0f}%")


def render_heatmap(df):
    """Render heatmap of wait times by hour and day."""
    st.header("🗺️ Wait Time Heatmap")

    if len(df) == 0:
        st.warning("No data available for the selected filters.")
        return

    # Create pivot table for heatmap
    heatmap_data = df.pivot_table(
        values='wait_time',
        index='day_of_week',
        columns='hour',
        aggfunc='mean'
    )

    # Rename index to day names
    heatmap_data.index = [DAY_NAMES[i] for i in heatmap_data.index]

    fig = px.imshow(
        heatmap_data,
        title="Average Wait Time: Hour vs Day of Week",
        labels={'x': 'Hour of Day', 'y': 'Day of Week', 'color': 'Wait (min)'},
        color_continuous_scale='RdYlGn_r',
        aspect='auto'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.info("🟢 Green = shorter waits (good time to visit) | 🔴 Red = longer waits (busy)")


def render_ride_comparison(df):
    """Render ride comparison view."""
    st.header("🎢 Ride Comparison")

    if len(df) == 0:
        st.warning("No data available for the selected filters.")
        return

    # Get top rides
    ride_stats = df.groupby(['ride_name', 'park_name']).agg({
        'wait_time': ['mean', 'std', 'max', 'min', 'count']
    }).round(1)
    ride_stats.columns = ['Avg', 'Std Dev', 'Max', 'Min', 'Count']
    ride_stats = ride_stats.sort_values('Avg', ascending=False).reset_index()

    # Top 15 rides chart
    top_15 = ride_stats.head(15)

    fig = px.bar(
        top_15,
        y='ride_name',
        x='Avg',
        color='park_name',
        orientation='h',
        title="Top 15 Rides by Average Wait Time",
        labels={'ride_name': '', 'Avg': 'Average Wait (min)', 'park_name': 'Park'},
        error_x='Std Dev'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Ride selector for detailed view
    st.subheader("📈 Detailed Ride Analysis")

    rides_list = sorted(df['ride_name'].unique())
    selected_rides = st.multiselect(
        "Select rides to compare",
        options=rides_list,
        default=rides_list[:3] if len(rides_list) >= 3 else rides_list,
        max_selections=5
    )

    if selected_rides:
        ride_data = df[df['ride_name'].isin(selected_rides)]

        # Hourly comparison
        hourly = ride_data.groupby(['hour', 'ride_name'])['wait_time'].mean().reset_index()

        fig = px.line(
            hourly,
            x='hour',
            y='wait_time',
            color='ride_name',
            title="Wait Times by Hour",
            labels={'hour': 'Hour', 'wait_time': 'Average Wait (min)', 'ride_name': 'Ride'},
            markers=True
        )
        fig.update_xaxes(tickmode='linear', tick0=0, dtick=2)
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# Main App
# =============================================================================

def main():
    """Main app entry point."""
    # Title
    st.title("🎢 Universal Orlando Wait Time Tracker")
    st.caption("Analyzing wait time patterns to find the best times to ride")

    # Load data
    parks_df, rides_df, wait_times_df = load_data()

    # Check if data exists
    if wait_times_df is None or len(wait_times_df) == 0:
        st.error("No data available yet. The database is empty or doesn't exist.")
        st.info("Run the collector to start gathering data: `python -m src.collector`")
        return

    # Sidebar filters
    filters = render_sidebar(wait_times_df, rides_df)

    # Apply filters
    filtered_df = apply_filters(wait_times_df, filters)

    # Show filter summary
    st.sidebar.divider()
    st.sidebar.caption(f"Showing {len(filtered_df):,} records")

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "⏰ By Hour",
        "📅 By Day",
        "🗺️ Heatmap",
        "🎢 Rides"
    ])

    with tab1:
        render_overview(filtered_df, parks_df, rides_df)

    with tab2:
        render_hourly_analysis(filtered_df)

    with tab3:
        render_daily_analysis(filtered_df)

    with tab4:
        render_heatmap(filtered_df)

    with tab5:
        render_ride_comparison(filtered_df)

    # Footer
    st.divider()
    st.caption(
        f"Data collected every 30 minutes via GitHub Actions. "
        f"Last updated: {wait_times_df['collected_at'].max().strftime('%Y-%m-%d %H:%M')} | "
        f"[GitHub](https://github.com/austinjamesrose/universal-wait-time-tracking-project)"
    )


if __name__ == "__main__":
    main()
