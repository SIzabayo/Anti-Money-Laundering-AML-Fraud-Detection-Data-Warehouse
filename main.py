import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import altair as alt
from functools import lru_cache
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AML & Fraud Detection Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    div[data-testid="metric-container"] {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    div[data-testid="metric-container"] > div {
        color: #1f2937;
    }
    .stDownloadButton button {
        background-color: #3b82f6;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection with connection pooling
@st.cache_resource
def get_engine():
    """Create cached database engine"""
    user = 'root'
    password = ''
    host = 'localhost'
    port = 3306
    database = 'aml_fraud_dw'
    
    return create_engine(
        f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}',
        poolclass=NullPool,
        pool_pre_ping=True
    )

engine = get_engine()

# Cached query functions for performance
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_kpi_metrics():
    """Fetch all KPI metrics in a single optimized query"""
    query = """
    SELECT 
        COUNT(*) as total_txn_count,
        SUM(t.amount) as total_txn_amount,
        SUM(CASE WHEN t.amount > 10000 THEN 1 ELSE 0 END) as high_value_count,
        SUM(CASE WHEN t.amount > 10000 THEN t.amount ELSE 0 END) as high_value_amount,
        SUM(CASE WHEN c.kyc_status = 'Incomplete' AND t.amount > 5000 THEN 1 ELSE 0 END) as suspicious_count,
        SUM(CASE WHEN c.kyc_status = 'Incomplete' AND t.amount > 5000 THEN t.amount ELSE 0 END) as suspicious_amount
    FROM transaction_fact t
    LEFT JOIN customer_dim c ON t.customer_id = c.customer_id
    """
    return pd.read_sql(query, engine).iloc[0]

@st.cache_data(ttl=300)
def get_monthly_trends():
    """Fetch monthly transaction trends"""
    query = """
    SELECT 
        d.year, 
        d.month, 
        COUNT(*) AS txn_count, 
        SUM(t.amount) AS total_amount
    FROM transaction_fact t
    JOIN date_dim d ON t.date_id = d.date_id
    GROUP BY d.year, d.month
    ORDER BY d.year, d.month
    """
    df = pd.read_sql(query, engine)
    df['period'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    return df

@st.cache_data(ttl=300)
def get_risk_distribution():
    """Fetch transactions by risk level"""
    query = """
    SELECT 
        c.risk_level,
        COUNT(*) as txn_count,
        SUM(t.amount) as total_amount
    FROM transaction_fact t
    JOIN customer_dim c ON t.customer_id = c.customer_id
    GROUP BY c.risk_level
    ORDER BY txn_count DESC
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def get_channel_distribution():
    """Fetch transactions by channel"""
    query = """
    SELECT 
        ch.channel_type,
        COUNT(*) as txn_count,
        SUM(t.amount) as total_amount
    FROM transaction_fact t
    JOIN channel_dim ch ON t.channel_id = ch.channel_id
    GROUP BY ch.channel_type
    ORDER BY txn_count DESC
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def get_top_customers():
    """Fetch top 10 most active customers"""
    query = """
    SELECT 
        c.name, 
        c.risk_level,
        COUNT(*) as txn_count,
        SUM(t.amount) as total_amount
    FROM transaction_fact t
    JOIN customer_dim c ON t.customer_id = c.customer_id
    GROUP BY c.customer_id, c.name, c.risk_level
    ORDER BY txn_count DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def get_foreign_transactions():
    """Fetch top 10 large foreign transactions"""
    query = """
    SELECT 
        t.transaction_id, 
        t.amount,
        t.origin_country, 
        t.destination_country,
        c.name as customer_name
    FROM transaction_fact t
    JOIN customer_dim c ON t.customer_id = c.customer_id
    WHERE t.origin_country <> t.destination_country
    ORDER BY t.amount DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

# Header
st.markdown('<div class="main-header">🛡️ AML & Fraud Detection Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Real-time monitoring and analytics | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

# KPI Metrics
st.subheader("📊 Key Performance Indicators")

with st.spinner('Loading metrics...'):
    kpis = get_kpi_metrics()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💳 Total Transactions",
        f"{int(kpis['total_txn_count']):,}",
        delta=f"${kpis['total_txn_amount']:,.2f} total volume"
    )

with col2:
    st.metric(
        "💰 High-Value Transactions",
        f"{int(kpis['high_value_count']):,}",
        delta=f"${kpis['high_value_amount']:,.2f} (>$10K)",
        delta_color="normal"
    )

with col3:
    st.metric(
        "⚠️ Suspicious Transactions",
        f"{int(kpis['suspicious_count']):,}",
        delta=f"${kpis['suspicious_amount']:,.2f} (Incomplete KYC + >$5K)",
        delta_color="inverse"
    )

st.markdown("---")

# Monthly Trends
st.subheader("📈 Transaction Trends Over Time")

with st.spinner('Loading trend data...'):
    txn_month = get_monthly_trends()

tab1, tab2 = st.tabs(["📊 Visualizations", "📋 Data Table"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        chart_count = alt.Chart(txn_month).mark_line(
            point=alt.OverlayMarkDef(filled=False, fill="white", size=80)
        ).encode(
            x=alt.X('period:N', title='Period', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('txn_count:Q', title='Transaction Count'),
            tooltip=[
                alt.Tooltip('period:N', title='Period'),
                alt.Tooltip('txn_count:Q', title='Count', format=','),
                alt.Tooltip('total_amount:Q', title='Volume', format='$,.2f')
            ]
        ).properties(
            title="Transaction Count by Month",
            height=300
        ).configure_mark(
            color='#3b82f6'
        )
        st.altair_chart(chart_count, use_container_width=True)
    
    with col2:
        chart_volume = alt.Chart(txn_month).mark_area(
            line={'color': '#f59e0b'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='white', offset=0),
                       alt.GradientStop(color='#fbbf24', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X('period:N', title='Period', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('total_amount:Q', title='Transaction Volume ($)'),
            tooltip=[
                alt.Tooltip('period:N', title='Period'),
                alt.Tooltip('txn_count:Q', title='Count', format=','),
                alt.Tooltip('total_amount:Q', title='Volume', format='$,.2f')
            ]
        ).properties(
            title="Transaction Volume by Month",
            height=300
        )
        st.altair_chart(chart_volume, use_container_width=True)

with tab2:
    st.dataframe(
        txn_month.style.format({
            'txn_count': '{:,}',
            'total_amount': '${:,.2f}'
        }),
        use_container_width=True
    )
    st.download_button(
        "📥 Download CSV",
        txn_month.to_csv(index=False),
        "monthly_trends.csv",
        "text/csv"
    )

st.markdown("---")

# Risk and Channel Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Transactions by Risk Level")
    with st.spinner('Loading risk data...'):
        df_risk = get_risk_distribution()
    
    chart_risk = alt.Chart(df_risk).mark_bar().encode(
        x=alt.X("risk_level:N", title="Risk Level", sort="-y"),
        y=alt.Y("txn_count:Q", title="Transaction Count"),
        color=alt.Color(
            "risk_level:N",
            scale=alt.Scale(
                domain=['Low', 'Medium', 'High'],
                range=['#10b981', '#f59e0b', '#ef4444']
            ),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("risk_level:N", title="Risk Level"),
            alt.Tooltip("txn_count:Q", title="Count", format=","),
            alt.Tooltip("total_amount:Q", title="Total Amount", format="$,.2f")
        ]
    ).properties(height=300)
    
    st.altair_chart(chart_risk, use_container_width=True)

with col2:
    st.subheader("📱 Transactions by Channel")
    with st.spinner('Loading channel data...'):
        df_channel = get_channel_distribution()
    
    chart_channel = alt.Chart(df_channel).mark_arc(innerRadius=50).encode(
        theta=alt.Theta("txn_count:Q"),
        color=alt.Color("channel_type:N", legend=alt.Legend(title="Channel")),
        tooltip=[
            alt.Tooltip("channel_type:N", title="Channel"),
            alt.Tooltip("txn_count:Q", title="Count", format=","),
            alt.Tooltip("total_amount:Q", title="Total Amount", format="$,.2f")
        ]
    ).properties(height=300)
    
    st.altair_chart(chart_channel, use_container_width=True)

st.markdown("---")

# Top Customers
st.subheader("👥 Top 10 Most Active Customers")

with st.spinner('Loading customer data...'):
    df_top = get_top_customers()

chart_top = alt.Chart(df_top).mark_bar().encode(
    x=alt.X("txn_count:Q", title="Transaction Count"),
    y=alt.Y("name:N", sort="-x", title="Customer Name"),
    color=alt.Color(
        "risk_level:N",
        scale=alt.Scale(
            domain=['Low', 'Medium', 'High'],
            range=['#10b981', '#f59e0b', '#ef4444']
        ),
        legend=alt.Legend(title="Risk Level")
    ),
    tooltip=[
        alt.Tooltip("name:N", title="Customer"),
        alt.Tooltip("risk_level:N", title="Risk Level"),
        alt.Tooltip("txn_count:Q", title="Transactions", format=","),
        alt.Tooltip("total_amount:Q", title="Total Amount", format="$,.2f")
    ]
).properties(height=400)

st.altair_chart(chart_top, use_container_width=True)

st.markdown("---")

# Foreign Transactions
st.subheader("🌍 Large Cross-Border Transactions")

with st.spinner('Loading foreign transactions...'):
    df_foreign = get_foreign_transactions()

st.dataframe(
    df_foreign.style.format({
        'amount': '${:,.2f}'
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Interactive OLAP Explorer
st.subheader("🔍 Interactive Data Explorer")

with st.expander("🔎 Click to explore transaction data by dimensions", expanded=False):
    st.info("💡 Select dimensions to join and explore your data interactively")
    
    join_map = {
        "Date": ("date_dim d", "t.date_id = d.date_id"),
        "Customer": ("customer_dim c", "t.customer_id = c.customer_id"),
        "Account": ("account_dim a", "t.account_id = a.account_id"),
        "Channel": ("channel_dim ch", "t.channel_id = ch.channel_id"),
    }
    
    dims = st.multiselect(
        "Select dimensions to explore",
        list(join_map.keys()),
        default=["Date"],
        help="Choose which dimensions to include in your analysis"
    )
    
    if dims:
        joins = ""
        selects = ["t.transaction_id", "t.amount"]
        for d in dims:
            table, cond = join_map[d]
            joins += f" LEFT JOIN {table} ON {cond}"
            alias = table.split()[-1]
            selects.append(f"{alias}.*")
        query = f"""
        SELECT {', '.join(selects)}
        FROM transaction_fact t
        {joins}
        LIMIT 5000
        """
        with st.spinner('Loading dimensional data...'):
            df = pd.read_sql(query, engine)
        st.success(f"✅ Loaded {len(df):,} transactions")
        # Pivot controls
        st.markdown("### 📊 Create Pivot Analysis")
        col1, col2, col3 = st.columns(3)
        # Only allow grouping by non-unique columns
        groupable_columns = [col for col in df.columns if col != "transaction_id"]
        with col1:
            index = st.selectbox("Group by:", groupable_columns, help="Select dimension to group by")
        with col2:
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            value = st.selectbox("Metric:", numeric_cols, help="Select metric to analyze")
        with col3:
            agg = st.selectbox("Aggregation:", ["sum", "mean", "count", "min", "max"])
        # Create pivot
        pivot = df.groupby(index, as_index=False)[value].agg(agg)
        pivot.columns = [index, f"{agg}_{value}"]
        # Display options
        tab1, tab2 = st.tabs(["📈 Chart", "📋 Data"])
        with tab1:
            chart_type = st.radio(
                "Chart type:",
                ["Bar", "Line", "Area"],
                horizontal=True
            )
            if chart_type == "Bar":
                chart = alt.Chart(pivot).mark_bar().encode(
                    x=alt.X(f"{index}:N", title=index),
                    y=alt.Y(f"{agg}_{value}:Q", title=f"{agg.title()} of {value}"),
                    tooltip=[index, f"{agg}_{value}"]
                ).properties(height=400)
            elif chart_type == "Line":
                chart = alt.Chart(pivot).mark_line(point=True).encode(
                    x=alt.X(f"{index}:N", title=index),
                    y=alt.Y(f"{agg}_{value}:Q", title=f"{agg.title()} of {value}"),
                    tooltip=[index, f"{agg}_{value}"]
                ).properties(height=400)
            else:
                chart = alt.Chart(pivot).mark_area().encode(
                    x=alt.X(f"{index}:N", title=index),
                    y=alt.Y(f"{agg}_{value}:Q", title=f"{agg.title()} of {value}"),
                    tooltip=[index, f"{agg}_{value}"]
                ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
        with tab2:
            st.dataframe(pivot, use_container_width=True)
            st.download_button(
                "📥 Download Pivot Data",
                pivot.to_csv(index=False),
                "pivot_analysis.csv",
                "text/csv"
            )

st.markdown("---")
st.caption("🛡️ AML & Fraud Detection Data Warehouse | Optimized Performance Dashboard")

# Add refresh button
if st.button("🔄 Refresh Data", help="Clear cache and reload all data"):
    st.cache_data.clear()
    st.rerun()