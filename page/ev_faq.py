"""
페이지 4. 기업 FAQ 조회
"""

import streamlit as st
from database.db import DBHandler


def show(ev_df, charger_df):
    st.header("❓ 기업 FAQ 조회")
    st.caption("전기차 관련 기업·기관의 자주 묻는 질문을 검색하세요.")

    db = DBHandler()

    try:
        sources_data = db.fetch_all(
            "SELECT DISTINCT source_name FROM faqs WHERE source_name IS NOT NULL ORDER BY source_name"
        )
        company_list = [row["source_name"] for row in sources_data]
    except Exception as e:
        st.error(f"DB 조회 실패: {e}")
        company_list = []

    if not company_list:
        st.warning("등록된 FAQ 데이터가 없습니다. 크롤러를 먼저 실행해주세요.")
        return

    col_a, col_b = st.columns([1, 2])
    with col_a:
        selected_company = st.selectbox("🏭 기업/기관 선택", company_list)
    with col_b:
        search_query = st.text_input("🔍 검색어 입력 (예: 보조금, 충전기, 배터리)")

    st.markdown("---")

    try:
        if search_query:
            faq_list = db.fetch_all(
                """SELECT category, question, answer FROM faqs
                   WHERE source_name = %s AND (question LIKE %s OR answer LIKE %s)
                   ORDER BY id DESC""",
                (selected_company, f"%{search_query}%", f"%{search_query}%")
            )
        else:
            faq_list = db.fetch_all(
                """SELECT category, question, answer FROM faqs
                   WHERE source_name = %s
                   ORDER BY id DESC LIMIT 30""",
                (selected_company,)
            )
    except Exception as e:
        st.error(f"FAQ 조회 실패: {e}")
        faq_list = []

    st.markdown(f"**{selected_company}** FAQ **{len(faq_list)}**건")

    if not faq_list:
        st.info("검색 결과가 없습니다. 다른 검색어를 입력해보세요.")
    else:
        for faq in faq_list:
            category_badge = f"`{faq['category']}` " if faq['category'] else ""
            with st.expander(f"❓ {category_badge}{faq['question']}"):
                st.write(faq["answer"])
