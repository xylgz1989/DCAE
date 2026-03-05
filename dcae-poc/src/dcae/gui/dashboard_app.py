"""
DCAE GUI Application
A Streamlit-based graphical interface for visualizing DCAE project status and metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import List, Dict, Tuple

# Import the existing dashboard functionality from dcae-poc
try:
    import sys
    from pathlib import Path
    # Add the dcae-poc source directory to the path
    poc_src = Path(__file__).parent.parent.parent.parent / "dcae-poc" / "src"
    sys.path.insert(0, str(poc_src))

    from dcae.stats.dashboard import PerformanceDashboard
    from dcae.stats.ui import ConsoleDashboardUI
    from dcae.stats.models import OperationType, PerformanceStatistics, AggregateStatistics
except ImportError:
    # Fallback for demo purposes
    class OperationType:
        CODE_GENERATION = "code_generation"
        CODE_REVIEW = "code_review"
        DEBUGGING = "debugging"
        REQUIREMENT_GEN = "requirement_generation"
        TEST_DOC_GEN = "test_documentation_generation"
        TEST_CASE_GEN = "test_case_generation"

    class PerformanceStatistics:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class AggregateStatistics:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # Mock dashboard classes for demonstration
    class MockPerformanceDashboard:
        def __init__(self):
            pass

        def get_aggregate_statistics(self, start_date, end_date):
            return AggregateStatistics(
                total_operations=100,
                successful_operations=85,
                failed_operations=15,
                success_rate=85.0,
                avg_duration_ms=2400.0,
                total_tokens_used=125000,
                total_api_calls=180,
                operations_by_type={OperationType.CODE_GENERATION: 40, OperationType.CODE_REVIEW: 25, OperationType.DEBUGGING: 20, OperationType.TEST_DOC_GEN: 15},
                success_rates_by_type={OperationType.CODE_GENERATION: 88.0, OperationType.CODE_REVIEW: 92.0, OperationType.DEBUGGING: 75.0, OperationType.TEST_DOC_GEN: 93.0}
            )

        def get_recent_operations(self, limit=10):
            operations = []
            for i in range(min(limit, 10)):
                operations.append(PerformanceStatistics(
                    operation_type=list(OperationType.__dict__.values())[i % 6] if i < 6 else OperationType.CODE_GENERATION,
                    operation_name=f"Operation {i+1}",
                    start_time=datetime.now() - timedelta(minutes=i*5),
                    success=random.choice([True, False]) if i < 3 else True,
                    tokens_used=random.randint(1000, 3000),
                    duration_ms=random.randint(1000, 5000)
                ))
            return operations

    PerformanceDashboard = MockPerformanceDashboard


def main():
    """Main function for the DCAE GUI application."""
    st.set_page_config(
        page_title="DCAE Dashboard",
        page_icon="📊",
        layout="wide"
    )

    # Add custom CSS for improved UI
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }

    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .info-box {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }

    .tab-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #444;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header section
    st.markdown('<div class="main-header">Distributed Coding Agent Environment (DCAE) Dashboard</div>', unsafe_allow_html=True)

    # Subheader with project information
    st.markdown("""
    <div class="info-box">
    <strong>Welcome to the DCAE Dashboard!</strong><br>
    Monitor and analyze your automated coding operations, track performance metrics, and manage documentation generation.
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("Navigation 🧭")
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Go to", ["Dashboard", "Projects", "Operations", "Documentation", "History", "Integrations"])

    # Add additional sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Tip: Use the navigation above to explore different aspects of your DCAE operations.")

    # Show last updated time
    st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize the dashboard
    dashboard = PerformanceDashboard()
    console_ui = ConsoleDashboardUI(dashboard) if 'ConsoleDashboardUI' in globals() else None

    if page == "Dashboard":
        show_dashboard(dashboard, console_ui)
    elif page == "Projects":
        show_projects_view(dashboard)
    elif page == "Operations":
        show_operations_view(dashboard)
    elif page == "Documentation":
        show_documentation_view(dashboard)
    elif page == "History":
        show_history_view(dashboard)
    elif page == "Integrations":
        show_integrations_view(dashboard)


def show_dashboard(dashboard, console_ui):
    """Display the main dashboard with key metrics."""
    st.title("📊 DCAE Dashboard")

    # Load aggregate statistics
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    if hasattr(dashboard, 'get_aggregate_statistics'):
        agg_stats = dashboard.get_aggregate_statistics(start_date, end_date)
    else:
        agg_stats = dashboard.get_aggregate_statistics(start_date, end_date)

    # Display summary cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(label="Total Operations", value=getattr(agg_stats, 'total_operations', 100))
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(label="Success Rate", value=f"{getattr(agg_stats, 'success_rate', 85.0):.1f}%",
                      delta="2%" if getattr(agg_stats, 'success_rate', 85.0) > 80 else "-1.5%")
            st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            avg_duration = getattr(agg_stats, 'avg_duration_ms', 2400)
            st.metric(label="Avg Duration", value=f"{avg_duration/1000:.1f}s")
            st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            tokens_used = getattr(agg_stats, 'total_tokens_used', 125000)
            st.metric(label="Tokens Used", value=f"{tokens_used:,}")
            st.markdown('</div>', unsafe_allow_html=True)

    # Create two main columns for charts
    left_col, right_col = st.columns(2)

    with left_col:
        # Operations by type chart
        if hasattr(agg_stats, 'operations_by_type'):
            op_types_data = []
            op_success_data = []
            for op_type, count in agg_stats.operations_by_type.items():
                op_types_data.append({
                    'Type': str(op_type).replace('_', ' ').title(),
                    'Count': count
                })

                # Add success rate data if available
                success_rate = agg_stats.success_rates_by_type.get(op_type, 0.0)
                op_success_data.append({
                    'Type': str(op_type).replace('_', ' ').title(),
                    'Success Rate': success_rate
                })

            if op_types_data:
                df_ops = pd.DataFrame(op_types_data)
                fig_ops = px.bar(df_ops, x='Type', y='Count', title="Operations by Type",
                                color='Type',
                                color_discrete_sequence=px.colors.qualitative.Set3)
                fig_ops.update_layout(height=400)
                st.plotly_chart(fig_ops, use_container_width=True)

                df_success = pd.DataFrame(op_success_data)
                fig_success = px.bar(df_success, x='Type', y='Success Rate',
                                    title="Success Rate by Operation Type",
                                    color='Type',
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_success.update_layout(height=400)
                st.plotly_chart(fig_success, use_container_width=True)
        else:
            # Demo data if real data not available
            demo_op_types = ["Code Gen", "Code Review", "Debugging", "Req Doc", "Test Doc"]
            demo_counts = [40, 25, 20, 10, 15]
            df_demo = pd.DataFrame({'Type': demo_op_types, 'Count': demo_counts})
            fig_demo = px.bar(df_demo, x='Type', y='Count', title="Operations by Type (Demo)",
                             color='Type',
                             color_discrete_sequence=px.colors.qualitative.Set3)
            fig_demo.update_layout(height=400)
            st.plotly_chart(fig_demo, use_container_width=True)

    with right_col:
        # Recent activity timeline
        if hasattr(dashboard, 'get_recent_operations'):
            recent_ops = dashboard.get_recent_operations(10)

            if recent_ops:
                activity_data = []
                for stat in recent_ops:
                    activity_data.append({
                        'Time': stat.start_time,
                        'Operation': str(getattr(stat, 'operation_type', 'Operation')).replace('_', ' ').title(),
                        'Success': '✅ Success' if getattr(stat, 'success', True) else '❌ Failed',
                        'Duration': getattr(stat, 'duration_ms', 0)/1000,
                        'Tokens': getattr(stat, 'tokens_used', 0)
                    })

                df_activity = pd.DataFrame(activity_data)
                fig_timeline = px.scatter(df_activity, x='Time', y='Operation', color='Success',
                                         size='Tokens', hover_data=['Duration'],
                                         title="Recent Activity Timeline",
                                         color_discrete_map={'✅ Success': '#2ECC40', '❌ Failed': '#FF4136'})
                fig_timeline.update_layout(height=400)
                st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            # Demo timeline
            demo_times = [datetime.now() - timedelta(hours=x) for x in range(10)]
            demo_ops = ["Code Gen", "Review", "Debug", "Req Doc", "Test Doc", "Code Gen", "Review", "Debug", "Test Doc", "Code Gen"]
            demo_success = ['✅ Success' if i < 8 else '❌ Failed' for i in range(10)]
            demo_tokens = [random.randint(1000, 3000) for _ in range(10)]

            df_demo_timeline = pd.DataFrame({
                'Time': demo_times,
                'Operation': demo_ops,
                'Success': demo_success,
                'Tokens': demo_tokens
            })

            fig_demo_timeline = px.scatter(df_demo_timeline, x='Time', y='Operation', color='Success',
                                          size='Tokens', title="Recent Activity Timeline (Demo)",
                                          color_discrete_map={'✅ Success': '#2ECC40', '❌ Failed': '#FF4136'})
            fig_demo_timeline.update_layout(height=400)
            st.plotly_chart(fig_demo_timeline, use_container_width=True)

    # Additional metrics section
    st.subheader("Additional Metrics", className="tab-header")
    metrics_col1, metrics_col2 = st.columns(2)

    with metrics_col1:
        st.info("Average tokens per operation: {:,.0f}".format(
            getattr(agg_stats, 'avg_tokens_per_operation', 1250)))
        st.info("Total API calls: {:,}".format(
            getattr(agg_stats, 'total_api_calls', 180)))

    with metrics_col2:
        st.info("Max operation duration: {:.1f}s".format(
            getattr(agg_stats, 'max_duration_ms', 5000)/1000))
        st.info("Min operation duration: {:.1f}s".format(
            getattr(agg_stats, 'min_duration_ms', 500)/1000))


def show_projects_view(dashboard):
    """Display project-specific information."""
    st.title("📁 Projects View")

    st.markdown("""
    <div class="info-box">
    This section displays information about individual projects and their metrics.
    Track project progress, success rates, and resource usage across your DCAE operations.
    </div>
    """, unsafe_allow_html=True)

    # Placeholder for future project-specific metrics
    st.info("Coming soon: Project-level breakdown of operations, success rates, and resource usage.")


def show_operations_view(dashboard):
    """Display detailed view by operation type."""
    st.title("⚙️ Operations View")

    st.markdown("""
    <div class="info-box">
    Detailed view of different operation types and their performance metrics.
    Compare performance across different operation categories and identify trends.
    </div>
    """, unsafe_allow_html=True)

    # Sample chart for operation comparison
    op_types = ['Code Generation', 'Code Review', 'Debugging', 'Requirements', 'Test Doc', 'Test Cases']
    success_rates = [88, 92, 75, 85, 93, 89]
    avg_durations = [2.3, 1.8, 4.2, 3.1, 2.7, 2.9]  # in seconds

    comparison_df = pd.DataFrame({
        'Operation': op_types,
        'Success Rate (%)': success_rates,
        'Avg Duration (s)': avg_durations
    })

    col1, col2 = st.columns(2)

    with col1:
        fig_success = px.bar(comparison_df, x='Operation', y='Success Rate (%)',
                             title="Success Rate by Operation Type",
                             color='Operation',
                             color_discrete_sequence=px.colors.qualitative.Vivid)
        fig_success.update_layout(height=400)
        st.plotly_chart(fig_success, use_container_width=True)

    with col2:
        fig_duration = px.bar(comparison_df, x='Operation', y='Avg Duration (s)',
                              title="Average Duration by Operation Type",
                              color='Operation',
                              color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_duration.update_layout(height=400)
        st.plotly_chart(fig_duration, use_container_width=True)


def show_documentation_view(dashboard):
    """Display documentation generation status and metrics."""
    st.title("📖 Documentation Status")

    # Load aggregate statistics to get documentation-related data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    if hasattr(dashboard, 'get_aggregate_statistics'):
        agg_stats = dashboard.get_aggregate_statistics(start_date, end_date)
    else:
        # Use mock data
        agg_stats = type('obj', (object,), {
            'operations_by_type': {OperationType.REQUIREMENT_GEN: 12, OperationType.TEST_DOC_GEN: 8},
            'success_rates_by_type': {OperationType.REQUIREMENT_GEN: 85.0, OperationType.TEST_DOC_GEN: 92.0},
            'total_operations': 100,
            'total_tokens_used': 125000
        })

    # Documentation status cards
    col1, col2, col3, col4 = st.columns(4)

    req_docs_count = agg_stats.operations_by_type.get(OperationType.REQUIREMENT_GEN, 0)
    test_docs_count = agg_stats.operations_by_type.get(OperationType.TEST_DOC_GEN, 0)

    with col1:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(label="Req Docs Generated", value=req_docs_count)
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            req_success_rate = agg_stats.success_rates_by_type.get(OperationType.REQUIREMENT_GEN, 0)
            st.metric(label="Req Doc Success Rate", value=f"{req_success_rate:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(label="Test Docs Generated", value=test_docs_count)
            st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            test_success_rate = agg_stats.success_rates_by_type.get(OperationType.TEST_DOC_GEN, 0)
            st.metric(label="Test Doc Success Rate", value=f"{test_success_rate:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)

    # Documentation progress visualization
    st.subheader("Documentation Progress", className="tab-header")

    # Create documentation completion progress
    doc_progress_data = [
        {"Type": "Requirements", "Progress": req_success_rate, "Target": 100},
        {"Type": "Test Documentation", "Progress": test_success_rate, "Target": 100},
    ]

    progress_df = pd.DataFrame(doc_progress_data)

    # Use gauge chart to show progress
    col1, col2 = st.columns(2)

    with col1:
        # Requirements documentation progress
        fig_req_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=req_success_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Requirements Documentation"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "#1f77b4"},
                   'steps': [{'range': [0, 50], 'color': "lightcoral"},
                             {'range': [50, 80], 'color': "khaki"},
                             {'range': [80, 100], 'color': "lightgreen"}],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}})
        )
        fig_req_gauge.update_layout(height=300)
        st.plotly_chart(fig_req_gauge, use_container_width=True)

    with col2:
        # Test documentation progress
        fig_test_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=test_success_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Test Documentation"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "#1f77b4"},
                   'steps': [{'range': [0, 50], 'color': "lightcoral"},
                             {'range': [50, 80], 'color': "khaki"},
                             {'range': [80, 100], 'color': "lightgreen"}],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}})
        )
        fig_test_gauge.update_layout(height=300)
        st.plotly_chart(fig_test_gauge, use_container_width=True)

    # Documentation quality metrics
    st.subheader("Documentation Quality Metrics", className="tab-header")

    # Sample data for documentation quality
    quality_metrics = {
        "Requirements Doc Quality": 87,
        "Test Doc Quality": 94,
        "Readability Score": 92,
        "Completeness Score": 88
    }

    # Create a bar chart for quality metrics
    quality_df = pd.DataFrame(list(quality_metrics.items()), columns=["Metric", "Score"])
    fig_quality = px.bar(quality_df, x="Score", y="Metric", orientation="h",
                         title="Documentation Quality Scores",
                         range_x=[0, 100],
                         color='Metric',
                         color_discrete_sequence=px.colors.qualitative.Light24)
    fig_quality.update_layout(height=400)
    st.plotly_chart(fig_quality, use_container_width=True)

    # Documentation activity over time
    st.subheader("Documentation Activity Trends", className="tab-header")

    # Generate sample documentation activity data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    req_docs = [random.randint(0, 3) for _ in dates]
    test_docs = [random.randint(0, 2) for _ in dates]

    doc_activity_df = pd.DataFrame({
        'Date': dates,
        'Requirements Docs': req_docs,
        'Test Docs': test_docs
    })

    # Line chart for documentation activity
    fig_doc_activity = px.line(doc_activity_df, x='Date', y=['Requirements Docs', 'Test Docs'],
                               title="Documentation Generation Over Time",
                               color_discrete_sequence=px.colors.qualitative.Set2)
    fig_doc_activity.update_layout(height=400)
    st.plotly_chart(fig_doc_activity, use_container_width=True)

    # Detailed documentation metrics
    st.subheader("Detailed Metrics", className="tab-header")

    st.write("**Requirements Documentation:**")
    st.progress(req_success_rate / 100, text=f"Success Rate: {req_success_rate:.1f}%")
    st.write("- Successfully generated:", req_docs_count, "documents")
    st.write("- Average tokens per document:", f"{(agg_stats.total_tokens_used // (req_docs_count or 1)) if hasattr(agg_stats, 'total_tokens_used') else 5000:,}")

    st.write("**Test Documentation:**")
    st.progress(test_success_rate / 100, text=f"Success Rate: {test_success_rate:.1f}%")
    st.write("- Successfully generated:", test_docs_count, "documents")
    st.write("- Average tokens per document:", f"{(agg_stats.total_tokens_used // (test_docs_count or 1)) if hasattr(agg_stats, 'total_tokens_used') else 6000:,}")


def show_integrations_view(dashboard):
    """Display integration with existing DCAE functionality."""
    st.title("🔗 DCAE Integrations")

    st.markdown("""
    <div class="info-box">
    This section shows integration with existing DCAE functionality and system components.
    Execute commands, manage configuration, and monitor system activity in real-time.
    </div>
    """, unsafe_allow_html=True)

    # Create tabs for different integration views
    tab1, tab2, tab3 = st.tabs(["DCAE CLI Commands", "Configuration", "Live Monitoring"])

    with tab1:
        st.subheader("DCAE CLI Commands", className="tab-header")

        # List of available DCAE commands with descriptions
        commands = {
            "init": "Initialize DCAE configuration",
            "gen": "Generate code from prompt",
            "review": "Review code file",
            "debug": "Debug an issue",
            "req": "Generate requirement document",
            "test-doc": "Generate test documentation",
            "test-case": "Generate test cases",
            "status": "Show DCAE status"
        }

        command_df = pd.DataFrame(list(commands.items()), columns=["Command", "Description"])

        st.dataframe(command_df, use_container_width=True)

        # Command execution interface
        st.subheader("Execute DCAE Command", className="tab-header")
        col1, col2 = st.columns([3, 1])

        with col1:
            command_input = st.selectbox("Select Command", options=list(commands.keys()))
            command_args = st.text_input("Arguments (optional)", placeholder="Enter command arguments")

        with col2:
            exec_button = st.button("Execute Command")

        if exec_button:
            st.info(f"Would execute: `python dcae.py {command_input} {command_args}`")
            st.warning("This is a simulation - actual command execution is not implemented in this demo.")

    with tab2:
        st.subheader("DCAE Configuration", className="tab-header")

        # Show configuration parameters
        config_params = {
            "Provider": "qwen",
            "Model Preference": "auto",
            "Daily Limit": "100,000 tokens",
            "Monthly Limit": "2,000,000 tokens",
            "Budget Mode": "token"
        }

        config_df = pd.DataFrame(list(config_params.items()), columns=["Parameter", "Value"])
        st.dataframe(config_df, use_container_width=True)

        st.info("Configuration settings can be modified through the DCAE configuration system.")

    with tab3:
        st.subheader("Live Monitoring", className="tab-header")

        # Simulate live monitoring of DCAE operations
        if st.button("Refresh Live Stats"):
            # In a real implementation, this would connect to the DCAE system
            st.success("Connected to DCAE system - live stats refreshed!")

        # Show simulated live stats
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Active Operations", 3, delta="+1")
        with col2:
            st.metric("System Health", "95%", delta="+2%")
        with col3:
            st.metric("Current Tokens/Hour", "1,200", delta="-50")

        # Live operations chart
        st.subheader("Current Operations", className="tab-header")

        # Generate simulated live data
        ops_types = ['gen', 'review', 'debug', 'req', 'test-doc']
        ops_counts = [random.randint(0, 10) for _ in ops_types]
        live_ops_df = pd.DataFrame({
            'Operation': [cmd.upper() for cmd in ops_types],
            'Count': ops_counts
        })

        fig_live_ops = px.bar(live_ops_df, x='Operation', y='Count',
                              title="Active Operations by Type",
                              color='Operation',
                              color_discrete_sequence=px.colors.qualitative.Bold)
        fig_live_ops.update_layout(height=400)
        st.plotly_chart(fig_live_ops, use_container_width=True)

        st.info("This section simulates real-time monitoring of DCAE operations. In a production system, this would connect directly to the DCAE process.")


def show_history_view(dashboard):
    """Display historical trends and analytics."""
    st.title("📈 History View")

    st.markdown("""
    <div class="info-box">
    Historical trends and analytics for DCAE operations.
    Analyze long-term performance, identify patterns, and track improvements over time.
    </div>
    """, unsafe_allow_html=True)

    # Generate sample historical data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    operations = [random.randint(2, 10) for _ in dates]
    success_rates = [random.uniform(70, 95) for _ in dates]
    tokens_used = [random.randint(2000, 8000) for _ in dates]

    history_df = pd.DataFrame({
        'Date': dates,
        'Operations': operations,
        'Success Rate (%)': success_rates,
        'Tokens Used': tokens_used
    })

    # Charts for historical data
    col1, col2 = st.columns(2)

    with col1:
        fig_ops = px.line(history_df, x='Date', y='Operations',
                         title="Daily Operations",
                         line_shape='linear',
                         color_discrete_sequence=['#1f77b4'])
        fig_ops.update_layout(height=400)
        st.plotly_chart(fig_ops, use_container_width=True)

    with col2:
        fig_success = px.line(history_df, x='Date', y='Success Rate (%)',
                             title="Success Rate Trend",
                             line_shape='linear',
                             color_discrete_sequence=['#2ca02c'])
        fig_success.update_layout(height=400)
        st.plotly_chart(fig_success, use_container_width=True)

    # Combined chart
    fig_combined = px.line(history_df, x='Date', y=['Operations', 'Success Rate (%)'],
                          title="Operations and Success Rate Over Time",
                          color_discrete_sequence=['#1f77b4', '#2ca02c'])
    fig_combined.update_layout(height=400)
    st.plotly_chart(fig_combined, use_container_width=True)


if __name__ == "__main__":
    main()