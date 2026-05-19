"""
페이지 2. 충전소 구축현황
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_folium import st_folium
from utils import (CHARGER_REGIONS, load_korea_geojson, make_charger_folium_map)


def show(ev_df, charger_df):
    st.header("🔌 전기차 충전기 구축현황")

    # ── 지역별 차트 ───────────────────────────────────────────
    col3, col4 = st.columns([1, 3])
    with col3:
        charger_regions = st.multiselect("지역 선택", CHARGER_REGIONS,
                                         default=["서울", "경기"], key="charger_region")
        speed_type      = st.radio("충전 속도", ["전체", "완속", "급속"], key="charger_speed")
        chart_type_ch   = st.radio("차트 유형", ["선 그래프", "막대 그래프"], key="charger_chart")
    with col4:
        if charger_regions:
            fig_ch = go.Figure()
            for region in charger_regions:
                col_name = f"{region}_{speed_type}"
                if col_name in charger_df.columns:
                    if chart_type_ch == "선 그래프":
                        fig_ch.add_trace(go.Scatter(
                            x=charger_df["년도"], y=charger_df[col_name],
                            mode="lines+markers", name=region,
                            line=dict(width=2), marker=dict(size=6)
                        ))
                    else:
                        fig_ch.add_trace(go.Bar(
                            x=charger_df["년도"], y=charger_df[col_name], name=region
                        ))
            fig_ch.update_layout(
                title=f"연도별 전기차 충전기 구축 수 ({speed_type}, 누적)",
                xaxis_title="년도", yaxis_title="충전기 수 (기)",
                hovermode="x unified", height=420, barmode="group"
            )
            st.plotly_chart(fig_ch, use_container_width=True)
        else:
            st.info("지역을 하나 이상 선택하세요.")

    # ── 완속 vs 급속 ──────────────────────────────────────────
    st.subheader("전국 완속 vs 급속 비교")
    fig_speed = go.Figure()
    fig_speed.add_trace(go.Bar(
        x=charger_df["년도"], y=charger_df["합계_완속"], name="완속", marker_color="#00CC96"
    ))
    fig_speed.add_trace(go.Bar(
        x=charger_df["년도"], y=charger_df["합계_급속"], name="급속", marker_color="#FF6692"
    ))
    fig_speed.update_layout(barmode="stack", xaxis_title="년도", yaxis_title="충전기 수 (기)",
                             hovermode="x unified", height=350)
    st.plotly_chart(fig_speed, use_container_width=True)

    # ── KPI ──────────────────────────────────────────────────
    latest_ch = charger_df.iloc[-1]
    prev_ch   = charger_df.iloc[-2]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("최신 기준 연도", latest_ch["년도"])
    c2.metric("전국 충전기 수", f"{int(latest_ch['합계_전체']):,} 기")
    c3.metric("전년 대비 증가",
              f"{int(latest_ch['합계_전체'] - prev_ch['합계_전체']):,} 기",
              delta=f"+{(latest_ch['합계_전체'] / prev_ch['합계_전체'] - 1) * 100:.1f}%")
    c4.metric("완속 / 급속 비율",
              f"{latest_ch['합계_완속'] / latest_ch['합계_전체'] * 100:.0f}% / "
              f"{latest_ch['합계_급속'] / latest_ch['합계_전체'] * 100:.0f}%")

    st.divider()

    # ── Folium 지도 ───────────────────────────────────────────
    st.subheader("🗺️ 지역별 충전기 현황 지도 (2025년 기준)")
    geojson     = load_korea_geojson()
    ch_row      = charger_df[charger_df["년도"] == "2025"].iloc[0]
    speed_label = st.radio("충전 속도", ["전체", "완속", "급속"], horizontal=True, key="map_speed")

    m_ch, ch_geo = make_charger_folium_map(geojson["features"], ch_row, speed_label)
    ch_map_df = pd.DataFrame([
        {"지역": f["properties"]["지역"], "충전기수": f["properties"]["value"]}
        for f in ch_geo["features"]
    ])

    map_l2, map_r2 = st.columns([1.1, 1])
    with map_l2:
        st_folium(m_ch, width=520, height=560, returned_objects=[])
    with map_r2:
        st.subheader("지역별 순위")
        ch_rank = ch_map_df.drop_duplicates().query("충전기수 > 0").sort_values("충전기수", ascending=False).reset_index(drop=True)
        ch_rank.index += 1
        ch_rank["충전기수"] = ch_rank["충전기수"].apply(lambda x: f"{x:,} 기")
        st.dataframe(ch_rank, use_container_width=True, height=560)

    with st.expander("📋 원본 데이터"):
        st.dataframe(charger_df, use_container_width=True)
