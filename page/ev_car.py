"""
페이지 1. 전기차 등록현황
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_folium import st_folium
from utils import (REGIONS, load_korea_geojson, make_ev_folium_map)


def show(ev_df, charger_df):
    st.header("🚗 전기차 등록현황")

    # ── 지역별 차트 ───────────────────────────────────────────
    col1, col2 = st.columns([1, 3])
    with col1:
        ev_regions    = st.multiselect("지역 선택", REGIONS,
                                       default=["서울", "경기", "인천"], key="ev_region")
        chart_type_ev = st.radio("차트 유형", ["선 그래프", "막대 그래프"], key="ev_chart")
    with col2:
        if ev_regions:
            fig_ev = go.Figure()
            for region in ev_regions:
                if region in ev_df.columns:
                    if chart_type_ev == "선 그래프":
                        fig_ev.add_trace(go.Scatter(
                            x=ev_df["년도"], y=ev_df[region],
                            mode="lines+markers", name=region,
                            line=dict(width=2), marker=dict(size=6)
                        ))
                    else:
                        fig_ev.add_trace(go.Bar(
                            x=ev_df["년도"], y=ev_df[region], name=region
                        ))
            fig_ev.update_layout(
                title="연도별 전기차 등록 대수 (누적)",
                xaxis_title="년도", yaxis_title="등록 대수 (대)",
                hovermode="x unified", height=420, barmode="group"
            )
            st.plotly_chart(fig_ev, use_container_width=True)
        else:
            st.info("지역을 하나 이상 선택하세요.")

    # ── 전국 합계 추이 ────────────────────────────────────────
    st.subheader("전국 합계 추이")
    fig_ev_total = go.Figure()
    fig_ev_total.add_trace(go.Bar(
        x=ev_df["년도"], y=ev_df["합계"], name="전국 합계", marker_color="#636EFA"
    ))
    fig_ev_total.add_trace(go.Scatter(
        x=ev_df["년도"], y=ev_df["합계"], mode="lines+markers", name="추이선",
        line=dict(color="#EF553B", width=2), marker=dict(size=7)
    ))
    fig_ev_total.update_layout(xaxis_title="년도", yaxis_title="등록 대수 (대)",
                                hovermode="x unified", height=350)
    st.plotly_chart(fig_ev_total, use_container_width=True)

    # ── KPI ──────────────────────────────────────────────────
    latest_ev = ev_df.iloc[-1]
    prev_ev   = ev_df.iloc[-2]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("최신 기준 연도", latest_ev["년도"])
    k2.metric("전국 등록 대수", f"{int(latest_ev['합계']):,} 대")
    k3.metric("전년 대비 증가",
              f"{int(latest_ev['합계'] - prev_ev['합계']):,} 대",
              delta=f"+{(latest_ev['합계'] / prev_ev['합계'] - 1) * 100:.1f}%")
    k4.metric("최다 등록 지역",
              ev_df[REGIONS].iloc[-1].idxmax(),
              f"{int(ev_df[REGIONS].iloc[-1].max()):,} 대")

    st.divider()

    # ── Folium 지도 ───────────────────────────────────────────
    st.subheader("🗺️ 지역별 등록현황 지도 (2025년 기준)")
    geojson = load_korea_geojson()
    ev_row  = ev_df[ev_df["년도"] == "2025"].iloc[0]

    m_ev, ev_geo = make_ev_folium_map(geojson["features"], ev_row)
    ev_map_df = pd.DataFrame([
        {"지역": f["properties"]["지역"], "등록대수": f["properties"]["value"]}
        for f in ev_geo["features"]
    ])

    map_l, map_r = st.columns([1.1, 1])
    with map_l:
        st_folium(m_ev, width=520, height=560, returned_objects=[])
    with map_r:
        st.subheader("지역별 순위")
        ev_rank = ev_map_df.sort_values("등록대수", ascending=False).reset_index(drop=True)
        ev_rank.index += 1
        ev_rank["등록대수"] = ev_rank["등록대수"].apply(lambda x: f"{x:,} 대")
        st.dataframe(ev_rank, use_container_width=True, height=560)

    with st.expander("📋 원본 데이터"):
        st.dataframe(ev_df, use_container_width=True)
