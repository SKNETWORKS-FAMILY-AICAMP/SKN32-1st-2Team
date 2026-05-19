"""
페이지 3. 전기차 vs 충전기 비교
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import EV_TO_REGION


def show(ev_df, charger_df):
    st.header("📊 전기차 등록 대수 vs 충전기 수 비교")

    common_years   = sorted(set(ev_df["년도"]) & set(charger_df["년도"]))
    ev_common      = ev_df[ev_df["년도"].isin(common_years)].set_index("년도")
    charger_common = charger_df[charger_df["년도"].isin(common_years)].set_index("년도")

    # ── 이중축 차트 ───────────────────────────────────────────
    fig_combo = go.Figure()
    fig_combo.add_trace(go.Bar(
        x=common_years, y=ev_common["합계"],
        name="전기차 등록 (대)", marker_color="#636EFA", opacity=0.7
    ))
    fig_combo.add_trace(go.Scatter(
        x=common_years, y=charger_common["합계_전체"],
        mode="lines+markers", name="충전기 수 (기)",
        line=dict(color="#EF553B", width=2), marker=dict(size=7)
    ))
    fig_combo.update_layout(
        title="전기차 등록 대수 vs 충전기 구축 수 (전국)",
        xaxis_title="년도",
        yaxis_title="수량",
        hovermode="x unified",
        height=450
    )
    st.plotly_chart(fig_combo, use_container_width=True)

    # ── 1대당 충전기 수 ───────────────────────────────────────
    ratio = (charger_common["합계_전체"] / ev_common["합계"]).reset_index()
    ratio.columns = ["년도", "충전기/전기차"]
    fig_ratio = px.line(ratio, x="년도", y="충전기/전기차",
                        title="전기차 1대당 충전기 수 (전국)", markers=True)
    fig_ratio.update_traces(line_color="#AB63FA", line_width=2, marker_size=7)
    fig_ratio.update_layout(yaxis_title="충전기 수 (기/대)", height=350)
    st.plotly_chart(fig_ratio, use_container_width=True)

    # ── KPI ──────────────────────────────────────────────────
    latest_ev = ev_df.iloc[-1]
    latest_ch = charger_df.iloc[-1]
    m1, m2, m3 = st.columns(3)
    m1.metric("전국 전기차 등록", f"{int(latest_ev['합계']):,} 대", f"기준: {latest_ev['년도']}년")
    m2.metric("전국 충전기 수",   f"{int(latest_ch['합계_전체']):,} 기", f"기준: {latest_ch['년도']}년")
    m3.metric("전기차 1대당 충전기",
              f"{latest_ch['합계_전체'] / latest_ev['합계']:.3f} 기/대")

    st.divider()

    # ── 연도별 증가율 ─────────────────────────────────────────
    st.header("📈 연도별 증가율")
    st.caption("전년 대비 전기차 등록 증가율 및 충전기 구축 증가율")

    ev_growth = ev_common["합계"].pct_change() * 100
    ch_growth = charger_common["합계_전체"].pct_change() * 100
    growth_df = pd.DataFrame({
        "년도":         common_years,
        "전기차 증가율": ev_growth.values,
        "충전기 증가율": ch_growth.values,
    }).dropna()

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        fig_ev_growth = go.Figure()
        fig_ev_growth.add_trace(go.Bar(
            x=growth_df["년도"], y=growth_df["전기차 증가율"],
            marker_color=["#636EFA" if v >= 0 else "#EF553B" for v in growth_df["전기차 증가율"]],
            text=[f"{v:.1f}%" for v in growth_df["전기차 증가율"]],
            textposition="outside",
        ))
        fig_ev_growth.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_ev_growth.update_layout(title="전기차 등록 전년 대비 증가율",
                                     xaxis_title="년도", yaxis_title="증가율 (%)",
                                     height=380, showlegend=False)
        st.plotly_chart(fig_ev_growth, use_container_width=True)

    with gcol2:
        fig_ch_growth = go.Figure()
        fig_ch_growth.add_trace(go.Bar(
            x=growth_df["년도"], y=growth_df["충전기 증가율"],
            marker_color=["#00CC96" if v >= 0 else "#EF553B" for v in growth_df["충전기 증가율"]],
            text=[f"{v:.1f}%" for v in growth_df["충전기 증가율"]],
            textposition="outside",
        ))
        fig_ch_growth.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_ch_growth.update_layout(title="충전기 구축 전년 대비 증가율",
                                     xaxis_title="년도", yaxis_title="증가율 (%)",
                                     height=380, showlegend=False)
        st.plotly_chart(fig_ch_growth, use_container_width=True)

    fig_growth_compare = go.Figure()
    fig_growth_compare.add_trace(go.Scatter(
        x=growth_df["년도"], y=growth_df["전기차 증가율"],
        mode="lines+markers", name="전기차 증가율",
        line=dict(color="#636EFA", width=2), marker=dict(size=7)
    ))
    fig_growth_compare.add_trace(go.Scatter(
        x=growth_df["년도"], y=growth_df["충전기 증가율"],
        mode="lines+markers", name="충전기 증가율",
        line=dict(color="#00CC96", width=2), marker=dict(size=7)
    ))
    fig_growth_compare.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_growth_compare.update_layout(
        title="전기차 등록 vs 충전기 구축 증가율 비교",
        xaxis_title="년도", yaxis_title="증가율 (%)",
        hovermode="x unified", height=400
    )
    st.plotly_chart(fig_growth_compare, use_container_width=True)

    with st.expander("📋 증가율 상세 수치"):
        disp = growth_df.copy()
        disp["전기차 증가율"] = disp["전기차 증가율"].apply(lambda x: f"{x:.1f}%")
        disp["충전기 증가율"] = disp["충전기 증가율"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(disp.set_index("년도"), use_container_width=True)

    st.divider()

    # ── 충전 취약 지역 TOP 3 ──────────────────────────────────
    st.header("⚠️ 충전 취약 지역 TOP 3")
    st.caption("전기차 1대당 충전기 수가 가장 낮은 권역 (충전 인프라 부족 지역)")

    latest_year = max(common_years)
    ev_row_v    = ev_df[ev_df["년도"] == latest_year].iloc[0]
    ch_row_v    = charger_df[charger_df["년도"] == latest_year].iloc[0]

    vuln_data = []
    for region, ev_cols in EV_TO_REGION.items():
        ev_total  = sum(int(ev_row_v[c]) for c in ev_cols if c in ev_row_v)
        ch_total  = int(ch_row_v[f"{region}_전체"])
        ratio_val = round(ch_total / ev_total, 4) if ev_total > 0 else 0
        vuln_data.append({
            "권역": region, "전기차 등록": ev_total,
            "충전기 수": ch_total, "1대당 충전기": ratio_val,
        })

    vuln_df = pd.DataFrame(vuln_data).sort_values("1대당 충전기").reset_index(drop=True)
    top3    = vuln_df.head(3)
    badges  = ["🥇", "🥈", "🥉"]
    cols    = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        cols[i].metric(
            label=f"{badges[i]} {row['권역']}",
            value=f"{row['1대당 충전기']:.4f} 기/대",
            delta=f"전기차 {int(row['전기차 등록']):,}대 / 충전기 {int(row['충전기 수']):,}기",
            delta_color="inverse"
        )
    st.caption(f"기준 연도: {latest_year}년 / 전체 충전기 기준")

    with st.expander("📋 원본 데이터"):
        tab1, tab2 = st.tabs(["전기차 등록현황", "충전기 구축현황"])
        with tab1:
            st.dataframe(ev_df, use_container_width=True)
        with tab2:
            st.dataframe(charger_df, use_container_width=True)
