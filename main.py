"""
전기차 현황 대시보드 (MySQL 연동 + Folium 지도 + 사이드바 메뉴 + FAQ)
실행: streamlit run main.py

의존성:
  pip install streamlit pandas plotly pymysql sqlalchemy requests folium streamlit-folium
"""

import streamlit as st
from utils import load_ev, load_charger
from page import ev_car, charger, compare, ev_faq

# ── 페이지 설정 ─────────────────────────────────────────────
st.set_page_config(page_title="지역별 전기차 충전 인프라 분석", page_icon="⚡", layout="wide")

# ── 사이드바 메뉴 ───────────────────────────────────────────
MENU_EV      = "🚗 전기차 등록현황"
MENU_CHARGER = "🔌 충전소 구축현황"
MENU_COMPARE = "📊 전기차 vs 충전기 비교"
MENU_FAQ     = "❓ 기업 FAQ 조회"

with st.sidebar:
    st.title("⚡ 메뉴")
    st.markdown("---")
    menu = st.radio(
        "페이지 선택",
        [MENU_EV, MENU_CHARGER, MENU_COMPARE, MENU_FAQ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("전기차 등록현황 + 충전기 구축현황\n년도별·지역별 분석 (MySQL 연동)")

# ── 타이틀 ─────────────────────────────────────────────────
st.title("⚡ 전국 전기차 등록 현황 및 충전소 설치 현황")
st.divider()

# ── 데이터 로드 ─────────────────────────────────────────────
try:
    ev_df      = load_ev()
    charger_df = load_charger()
    if ev_df.empty or charger_df.empty:
        st.warning("DB에 데이터가 없습니다. ev_stats_db.py를 먼저 실행하세요.")
        st.stop()
except Exception as e:
    st.error(f"DB 연결 실패: {e}")
    st.info("PASSWORD를 확인하고 ev_stats_db.py를 먼저 실행했는지 확인하세요.")
    st.stop()

# ── 페이지 라우팅 ───────────────────────────────────────────
if menu == MENU_EV:
    ev_car.show(ev_df, charger_df)

elif menu == MENU_CHARGER:
    charger.show(ev_df, charger_df)

elif menu == MENU_COMPARE:
    compare.show(ev_df, charger_df)

elif menu == MENU_FAQ:
    ev_faq.show(ev_df, charger_df)