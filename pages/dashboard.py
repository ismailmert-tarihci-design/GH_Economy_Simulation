"""
Dashboard page for the Bluestar Economy Simulator.

Displays interactive Plotly charts:
- Chart 1: Bluestar Accumulation Curve (deterministic line or MC mean + 95% CI band)
- Chart 2: Card Progression by Category (3 category lines + max level reference lines)
"""

from typing import Any

import plotly.graph_objects as go
import streamlit as st


def render_dashboard() -> None:
    """Render dashboard with Bluestar and card progression charts."""
    if "sim_result" not in st.session_state:
        st.warning("⚠️ No simulation results available. Run a simulation first.")
        return

    result = st.session_state.sim_result
    mode = st.session_state.sim_mode

    st.title("📊 Simulation Dashboard")

    _render_bluestar_chart(result, mode)
    _render_card_progression_chart(result, mode)


def _render_bluestar_chart(result: Any, mode: str) -> None:
    """
    Chart 1: Bluestar accumulation over time.

    Deterministic: Single line from daily_snapshots[i].total_bluestars
    Monte Carlo: Mean line + shaded 95% CI band (mean ± 1.96 * std)

    Args:
        result: SimResult or MCResult from simulation
        mode: "deterministic" or "monte_carlo"
    """
    fig = go.Figure()

    if mode == "deterministic":
        # Extract total_bluestars from daily_snapshots (0-indexed, day 1 at index 0)
        snapshots = result.daily_snapshots
        days = list(range(1, len(snapshots) + 1))  # 1-indexed display
        bluestars = [snapshot.total_bluestars for snapshot in snapshots]

        fig.add_trace(
            go.Scatter(
                x=days,
                y=bluestars,
                mode="lines",
                name="Total Bluestars",
                line=dict(color="rgb(31, 119, 180)", width=2),
            )
        )

    else:  # monte_carlo
        # Use daily_bluestar_means and daily_bluestar_stds (0-indexed)
        means = result.daily_bluestar_means
        stds = result.daily_bluestar_stds
        days = list(range(1, len(means) + 1))  # 1-indexed display

        # Calculate 95% CI bounds
        upper = [m + 1.96 * s for m, s in zip(means, stds)]
        lower = [m - 1.96 * s for m, s in zip(means, stds)]

        # Create filled polygon for confidence interval (x forward + x backward)
        x_combined = days + days[::-1]
        y_combined = upper + lower[::-1]

        fig.add_trace(
            go.Scatter(
                x=x_combined,
                y=y_combined,
                fill="toself",
                fillcolor="rgba(31, 119, 180, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="95% CI",
                showlegend=True,
                hoverinfo="skip",
            )
        )

        # Add mean line on top of CI band
        fig.add_trace(
            go.Scatter(
                x=days,
                y=means,
                mode="lines",
                name="Mean Bluestars",
                line=dict(color="rgb(31, 119, 180)", width=2),
            )
        )

    fig.update_layout(
        title="Bluestar Accumulation Over Time",
        xaxis=dict(title="Day"),
        yaxis=dict(title="Total Bluestars"),
        hovermode="x unified",
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_card_progression_chart(result: Any, mode: str) -> None:
    """
    Chart 2: Average card level by category.

    Shows 3 lines: Gold Shared, Blue Shared, Unique (different colors)
    Deterministic: from daily_snapshots[i].category_avg_levels
    Monte Carlo: from daily_category_level_means (mean lines per category, no CI bands)
    Adds horizontal reference lines at max levels (Shared=100, Unique=10)

    Args:
        result: SimResult or MCResult from simulation
        mode: "deterministic" or "monte_carlo"
    """
    fig = go.Figure()

    # Color scheme for categories
    COLORS = {
        "GOLD_SHARED": "#FFD700",  # Bright gold
        "BLUE_SHARED": "#4169E1",  # Royal blue
        "UNIQUE": "#FF4500",  # Orange-red
    }

    # Display names for legend
    DISPLAY_NAMES = {
        "GOLD_SHARED": "Gold Shared",
        "BLUE_SHARED": "Blue Shared",
        "UNIQUE": "Unique",
    }

    if mode == "deterministic":
        # Extract category_avg_levels from daily_snapshots
        snapshots = result.daily_snapshots
        days = list(range(1, len(snapshots) + 1))  # 1-indexed display

        # Build data series for each category
        category_data = {
            "GOLD_SHARED": [],
            "BLUE_SHARED": [],
            "UNIQUE": [],
        }

        for snapshot in snapshots:
            for category in category_data.keys():
                # category_avg_levels is Dict[str, float]
                category_data[category].append(
                    snapshot.category_avg_levels.get(category, 0.0)
                )

        # Add line for each category
        for category in ["GOLD_SHARED", "BLUE_SHARED", "UNIQUE"]:
            fig.add_trace(
                go.Scatter(
                    x=days,
                    y=category_data[category],
                    mode="lines",
                    name=DISPLAY_NAMES[category],
                    line=dict(color=COLORS[category], width=2),
                )
            )

    else:  # monte_carlo
        # Use daily_category_level_means: Dict[str, List[float]]
        means_by_category = result.daily_category_level_means
        num_days = len(
            next(iter(means_by_category.values()))
        )  # Get length from first category
        days = list(range(1, num_days + 1))  # 1-indexed display

        # Add line for each category
        for category in ["GOLD_SHARED", "BLUE_SHARED", "UNIQUE"]:
            if category in means_by_category:
                fig.add_trace(
                    go.Scatter(
                        x=days,
                        y=means_by_category[category],
                        mode="lines",
                        name=DISPLAY_NAMES[category],
                        line=dict(color=COLORS[category], width=2),
                    )
                )

    # Add horizontal reference lines for max levels
    num_days = len(days)
    max_day = days[-1]

    # Shared max level = 100 (applies to both Gold and Blue Shared)
    fig.add_trace(
        go.Scatter(
            x=[1, max_day],
            y=[100, 100],
            mode="lines",
            name="Shared Max (100)",
            line=dict(color="gray", width=1, dash="dash"),
            showlegend=True,
        )
    )

    # Unique max level = 10
    fig.add_trace(
        go.Scatter(
            x=[1, max_day],
            y=[10, 10],
            mode="lines",
            name="Unique Max (10)",
            line=dict(color="darkgray", width=1, dash="dash"),
            showlegend=True,
        )
    )

    fig.update_layout(
        title="Average Card Level by Category",
        xaxis=dict(title="Day"),
        yaxis=dict(title="Average Card Level"),
        hovermode="x unified",
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)
