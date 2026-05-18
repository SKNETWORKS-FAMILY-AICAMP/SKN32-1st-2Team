# ⚡ 지역별 전기차 충전 인프라 분석 및 기업 전기차 관련FAQ

> 전국 전기차 등록 현황과 충전기 구축 현황을 정적 크롤링하여 년도별·지역별 대시보드로 시각화, 충전 인프라 분석 \n
> 기업 FAQ를 동적 크롤링하여 기업별 FAQ 검색 및 조회 (키워드 검색 지원)

---

## 📌 프로젝트 개요

- **프로젝트 명**: 지역별 전기차 충전 인프라 분석 및 기업 전기차 관련FAQ
- **프로젝트 기간**: 2026.05.18 ~ 2026.05.19
- **프로젝트 목표**
  - 년도별·지역별 전기차 등록 현황 및 충전기 구축 현황 분석
  - 충전 인프라 부족 지역 분석
  - 기업 FAQ 조회 및 검색

---

## 👨‍👩‍👧‍👦 팀 소개
- **팀명**: 🚗부릉데이터

**👥 팀원 및 역할**

| 팀원 | 역할 |
|------|------|
| 이태혁 | 팀장, DB 및 GUI 구현 |
| 문건일 | 기업 FAQ 동적 크롤링 |
| 박수진 | 전기차 등록 대수 및 충전소 현황 크롤링, 분석 및 비교, GUI 구현 |
| 소성민 | 기업 FAQ 동적 크롤링, 발표|
| 정세환 | 전기차 등록 대수 및 충전소 현황 크롤링, 분석 및 비교, 발표 |

---


## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| 언어 | Python 3.12 |
| 크롤링 | Requests, BeautifulSoup, Selenium |
| 데이터 처리 | Pandas, OpenPyXL |
| DB | MySQL 8.0, SQLAlchemy, PyMySQL |
| 시각화 | Streamlit, Plotly |
| 버전 관리 | Git, GitHub |

---

## 📂 프로젝트 구조

```
team_project_1/
│
├── car_stats.py                    # 전기차 등록현황 정적 크롤링 → CSV 변환
├── charger_stats.py                # 충전기 구축현황 정적 크롤링 → CSV 변환
├── ev_stats_db.py                  # CSV → MySQL 적재
├── FAQ.py                          # 기아자동차 FAQ 동적 크롤링
├── FAQ_hyn.py                      # 현대자동차 FAQ 동적 크롤링
├── db.py                           # DB 연결 설정 (DBHandler)
├── DashBoard.py                    # Streamlit 대시보드
│
├── 전기차등록현황_년도별지역별.csv
├── 전기차충전기_년도별지역별.csv
│
└── README.md


```
**사용 모듈**
- streamlit pandas plotly pymysql sqlalchemy openpyxl requests folium streamlit-folium selenium

## 📊 주요 기능

### 🚗 전기차 등록현황
- 지역별 연도별 등록 대수 선/막대 그래프
- 전국 합계 추이 차트
- 최신 연도 KPI 지표 (전국 등록 대수, 전년 대비 증가, 최다 등록 지역)
- 시도별 Choropleth 지도 시각화

### 🔌 충전소 구축현황
- 권역별 연도별 충전기 수 선/막대 그래프 (완속/급속/전체 필터)
- 전국 완속 vs 급속 스택 막대 차트
- 최신 연도 KPI 지표
- 권역별 Choropleth 지도 시각화

### 📊 전기차 vs 충전기 비교
- 전기차 등록 대수 vs 충전기 수 이중축 차트
- 전기차 1대당 충전기 수 추이
- 연도별 전기차·충전기 증가율 비교
- ⚠️ 충전 취약 지역 TOP 3 (1대당 충전기 수 최하위 권역)

### 💬기업 FAQ 조회
- 현대·기아자동차 FAQ 동적 크롤링 후 DB 저장
- 기업별 FAQ 검색 및 조회 (키워드 검색 지원)

**수집 대상**

| 기업 | URL | 크롤링 방식 |
|------|-----|------------|
| 현대자동차 | https://www.hyundai.com/kr/ko/e/customer/center/faq | Selenium (동적) |
| 기아자동차 | https://www.kia.com/kr/customer-service/center/faq | Selenium (동적) |

**수집 항목**

| 컬럼 | 설명 |
|------|------|
| source_name | 기업명 (현대 FAQ / 기아 FAQ) |
| category | FAQ 카테고리 |
| question | 질문 |
| answer | 답변 |
| question_hash | 중복 방지용 해시값 |
| crawled_at | 크롤링 일시 |

## 📑 시스템 데이터 명세서

### 1.1 데이터 수집 및 방법
- 전기차 등록 현황 및 충전 인프라 데이터
  - 공공데이터포털 등에서 제공하는 전국 전기차 등록 현황 및 충전소 구축 관련 원천 CSV 파일 활용
  - evcar.py 스크립트를 통해 CSV 데이터를 파싱 및 정제한 후, MySQL 데이터베이스의 ev_registration 및 ev_charger 테이블에 적재
- 추가 FAQ 및 안내 데이터 (동적 크롤링)
  - FAQ.py 및 FAQ_hyn.py 내부에서 Selenium을 활용하여 무공해차 통합누리집, 기아, 현대자동차 공식 FAQ 페이지에서 수집
  - 수집된 데이터를 주기적으로 배치를 통해 MySQL 데이터베이스의 faqs 테이블에 실시간 동기화 및 적재

### 1.2 수집 데이터 항목 명세
- 전기차 등록 정보 (ev_registration)
  - 기준 연도, 전국 17개 행정구역(서울~제주)별 전기차 순수 등록 대수, 전국 총 합계
- 충전 인프라 정보 (ev_charger)
  - 기준 연도, 지역별 완속 충전기 수, 급속 충전기 수, 총 합계
- FAQ 정보 (faqs)
  - FAQ 고유 식별자, 수집 출처 기관명, 원본 출처 URL, 카테고리, 질문, 답변, 고유 해시값, 데이터 갱신 시점

### 1.3 데이터 전처리
- CSV 로드 시 연도가 소수점(예: 2025.0) 형태로 왜곡되지 않도록 4자리 문자열 포맷으로 고정 처리
- 문자열(Object) 타입으로 인식되던 시도별 등록 대수 및 충전기 수를 대시보드 통계 연산이 가능하도록 정수형 데이터로 일괄 변환

---

## 📋 데이터 출처

- 전기차 등록현황: [국토교통부 자동차 등록 통계](https://www.data.go.kr)
- 전기차 충전기 구축현황: [환경부 전기차 충전 인프라 통계](https://www.data.go.kr)
---

## 🖋️ 프로젝트 회고

### 😊 이태혁
ooooooooooooooooooooooooooooooooooooooooooo
### 😊 문건민
ooooooooooooooooooooooooooooooooooooooooooo
### 😊 박수진
ooooooooooooooooooooooooooooooooooooooooooo
### 😊 소성민
ooooooooooooooooooooooooooooooooooooooooooo
### 😊 정세환
ooooooooooooooooooooooooooooooooooooooooooo
