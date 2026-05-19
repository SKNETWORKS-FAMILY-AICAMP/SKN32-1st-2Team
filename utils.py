"""
공통 상수 및 함수 모음
"""

import streamlit as st
import pandas as pd
import folium
import requests
from sqlalchemy import create_engine

# ── DB 연결 설정 ────────────────────────────────────────────
HOST     = "localhost"
PORT     = 3306
USER     = "student"
PASSWORD = "student80"
DATABASE = "ev_database"

# ── 지역 상수 ───────────────────────────────────────────────
REGIONS         = ["서울", "부산", "대구", "인천", "광주", "대전", "울산",
                   "세종", "경기", "강원", "충북", "충남", "전북", "전남",
                   "경북", "경남", "제주"]
CHARGER_REGIONS = ["서울", "경기", "인천", "강원", "충청", "전라", "경상", "제주"]

EV_NAME_MAP = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
    "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
    "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기",
    "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전북특별자치도": "전북", "전라남도": "전남", "경상북도": "경북",
    "경상남도": "경남", "제주특별자치도": "제주",
    "강원도": "강원", "전라북도": "전북", "제주도": "제주",
}
CHARGER_NAME_MAP = {
    "서울특별시": "서울", "경기도": "경기", "인천광역시": "인천",
    "강원특별자치도": "강원",
    "충청북도": "충청", "충청남도": "충청", "대전광역시": "충청", "세종특별자치시": "충청",
    "전라북도": "전라", "전북특별자치도": "전라", "전라남도": "전라", "광주광역시": "전라",
    "경상북도": "경상", "경상남도": "경상", "대구광역시": "경상",
    "부산광역시": "경상", "울산광역시": "경상",
    "제주특별자치도": "제주",
    "강원도": "강원", "제주도": "제주",
}
EV_TO_REGION = {
    "서울": ["서울"], "경기": ["경기"], "인천": ["인천"], "강원": ["강원"],
    "충청": ["충북", "충남", "대전", "세종"],
    "전라": ["전북", "전남", "광주"],
    "경상": ["경북", "경남", "대구", "부산", "울산"],
    "제주": ["제주"],
}
EV_COORDS = {
    "서울": (37.5665, 126.9780), "부산": (35.1796, 129.0756),
    "대구": (35.8714, 128.6014), "인천": (37.4563, 126.7052),
    "광주": (35.1595, 126.8526), "대전": (36.3504, 127.3845),
    "울산": (35.5384, 129.3114), "세종": (36.4800, 127.2890),
    "경기": (37.4138, 127.5183), "강원": (37.8228, 128.1555),
    "충북": (36.8000, 127.7000), "충남": (36.5184, 126.8000),
    "전북": (35.7175, 127.1530), "전남": (34.8679, 126.9910),
    "경북": (36.4919, 128.8889), "경남": (35.4606, 128.2132),
    "제주": (33.4996, 126.5312),
}
CHARGER_COORDS = {
    "서울": (37.5665, 126.9780), "경기": (37.4138, 127.5183),
    "인천": (37.4563, 126.7052), "강원": (37.8228, 128.1555),
    "충청": (36.5000, 127.2500), "전라": (35.3000, 126.9500),
    "경상": (35.8000, 128.5000), "제주": (33.4996, 126.5312),
}


# ── DB 연결 & 데이터 로드 ───────────────────────────────────
@st.cache_resource
def get_engine():
    url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"
    return create_engine(url)

@st.cache_data(ttl=300)
def load_ev():
    return pd.read_sql("SELECT * FROM ev_registration ORDER BY 년도",
                       get_engine(), dtype={"년도": str})

@st.cache_data(ttl=300)
def load_charger():
    return pd.read_sql("SELECT * FROM ev_charger ORDER BY 년도",
                       get_engine(), dtype={"년도": str})

@st.cache_data
def load_korea_geojson():
    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2018/json/skorea-provinces-2018-geo.json"
    return requests.get(url).json()


# ── Folium 지도 생성 함수 ────────────────────────────────────
def make_ev_folium_map(geo_features, ev_row):
    m = folium.Map(
        location=[36.0, 127.6], zoom_start=7,
        tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
        attr="CartoDB"
    )
    geo = {"type": "FeatureCollection", "features": []}
    for feat in geo_features:
        name_kr = feat["properties"].get("name", "")
        mapped  = EV_NAME_MAP.get(name_kr)
        value   = int(ev_row[mapped]) if mapped and mapped in ev_row else 0
        nf = dict(feat)
        nf["properties"] = {
            "name": name_kr, "short_name": mapped or name_kr,
            "지역": mapped or name_kr, "value": value
        }
        geo["features"].append(nf)

    folium.GeoJson(
        geo,
        style_function=lambda x: {"fillColor": "#ffffff", "color": "#ADC6FF", "weight": 1.5, "fillOpacity": 1.0},
        highlight_function=lambda x: {"fillColor": "#5B8FF9", "color": "#1D4ED8", "weight": 2.5, "fillOpacity": 0.85},
        tooltip=folium.features.GeoJsonTooltip(
            fields=["short_name", "value"], aliases=["지역: ", "등록대수(대): "],
            localize=True, sticky=False,
            style="font-family:'Malgun Gothic'; font-size:13px; background:#fff; border:1px solid #ADC6FF; border-radius:4px; padding:8px;"
        )
    ).add_to(m)

    for region, (lat, lon) in EV_COORDS.items():
        val = int(ev_row[region]) if region in ev_row else 0
        pin_html = f"""
        <div style="background:#9BD363; color:white; font-family:'Malgun Gothic';
                    font-size:12px; font-weight:bold; text-align:center;
                    padding:4px 8px; border-radius:6px; box-shadow:1px 2px 4px rgba(0,0,0,0.15);
                    white-space:nowrap;">
            {region}<br><span style="font-size:11px">{val:,}대</span>
            <div style="position:absolute; bottom:-6px; left:50%; transform:translateX(-50%);
                        width:0; height:0; border-left:6px solid transparent;
                        border-right:6px solid transparent; border-top:6px solid #9BD363;"></div>
        </div>"""
        folium.map.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(icon_size=(80, 40), icon_anchor=(40, 40), html=pin_html)
        ).add_to(m)

    return m, geo


def make_charger_folium_map(geo_features, ch_row, speed_label):
    m = folium.Map(
        location=[36.0, 127.6], zoom_start=7,
        tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
        attr="CartoDB"
    )
    geo = {"type": "FeatureCollection", "features": []}
    for feat in geo_features:
        name_kr = feat["properties"].get("name", "")
        mapped  = CHARGER_NAME_MAP.get(name_kr)
        col_key = f"{mapped}_{speed_label}" if mapped else None
        value   = int(ch_row[col_key]) if col_key and col_key in ch_row else 0
        nf = dict(feat)
        nf["properties"] = {
            "name": name_kr, "short_name": mapped or name_kr,
            "지역": mapped or name_kr, "value": value
        }
        geo["features"].append(nf)

    folium.GeoJson(
        geo,
        style_function=lambda x: {"fillColor": "#ffffff", "color": "#FFBB96", "weight": 1.5, "fillOpacity": 1.0},
        highlight_function=lambda x: {"fillColor": "#FF7A45", "color": "#D4380D", "weight": 2.5, "fillOpacity": 0.85},
        tooltip=folium.features.GeoJsonTooltip(
            fields=["short_name", "value"], aliases=["지역: ", "충전기수(기): "],
            localize=True, sticky=False,
            style="font-family:'Malgun Gothic'; font-size:13px; background:#fff; border:1px solid #FFBB96; border-radius:4px; padding:8px;"
        )
    ).add_to(m)

    for region, (lat, lon) in CHARGER_COORDS.items():
        col_key = f"{region}_{speed_label}"
        val = int(ch_row[col_key]) if col_key in ch_row else 0
        pin_html = f"""
        <div style="background:#FF9C6E; color:white; font-family:'Malgun Gothic';
                    font-size:12px; font-weight:bold; text-align:center;
                    padding:4px 8px; border-radius:6px; box-shadow:1px 2px 4px rgba(0,0,0,0.15);
                    white-space:nowrap;">
            {region}<br><span style="font-size:11px">{val:,}기</span>
            <div style="position:absolute; bottom:-6px; left:50%; transform:translateX(-50%);
                        width:0; height:0; border-left:6px solid transparent;
                        border-right:6px solid transparent; border-top:6px solid #FF9C6E;"></div>
        </div>"""
        folium.map.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(icon_size=(80, 40), icon_anchor=(40, 40), html=pin_html)
        ).add_to(m)

    return m, geo
