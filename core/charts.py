"""Plotly helpers that follow the LoanLens tokens."""
import plotly.graph_objects as go
import streamlit as st

from core.theme import CORAL, INK, LINE, MUTED, TEAL

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


CHART_HEIGHT = 300  # every chart uses the same plot size so cards line up


def style(fig: go.Figure, height: int = CHART_HEIGHT, y_title: str | None = None,
          x_title: str | None = None, legend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=30, b=8),  # fixed top margin holds the legend when there is one
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Onest, sans-serif", size=13, color=INK),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=1, xanchor="right", title=None,
                    bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="white", font_family="Onest, sans-serif"),
        bargap=0.35,
    )
    fig.update_xaxes(title=x_title, showgrid=False, linecolor=LINE, tickfont=dict(color=MUTED))
    fig.update_yaxes(title=y_title, gridcolor=LINE, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)


def rate_bar(df, x: str, y: str = "Refusal_Rate", highlight: str | None = None) -> go.Figure:
    """Refusal-rate bars; the highest bar is coral, the rest ink."""
    top = df[y].max()
    colors = [CORAL if v == top else INK for v in df[y]]
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y], marker_color=colors, marker_cornerradius=8,
        text=[f"{v:.1f}%" for v in df[y]], textposition="outside", cliponaxis=False,
        customdata=df["Applications"],
        hovertemplate="%{x}<br>Refusal rate: %{y:.1f}%<br>Applications: %{customdata:,}<extra></extra>",
    ))
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    return fig


STATUS_COLORS = {"Approved": TEAL, "Refused": CORAL}
