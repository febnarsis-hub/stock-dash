import hashlib
import hmac
import json
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from automatic import brief
from data_registry import PROVIDERS, capabilities as active_capabilities, health_all
from education import render_education
from portfolio_ui import render_portfolio
from providers import DataError, Official, demo
from research_ui import render_research
from storage import Store
from ui_v2 import apply_theme, brand, card, empty_state, hero, source_badge
from valuation_v22 import calculate_v22


load_dotenv()
st.set_page_config(
    page_title="StockDash · PlanX Investment OS",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    for key in [
        "APP_PASSWORD",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "DATA_GO_KR_SERVICE_KEY",
        "DART_CRTFC_KEY",
        "KRX_AUTH_KEY",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "KIS_ENV", "KIS_APP_KEY", "KIS_APP_SECRET", "KIS_CANO", "KIS_ACNT_PRDT_CD",
    ]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except FileNotFoundError:
    pass

apply_theme()


class SessionStore:
    cloud = False

    def read(self):
        return st.session_state.setdefault("practice_data", {"stocks": [], "journal": [], "runs": []})

    def save_stock(self, stock):
        data = self.read()
        for index, old in enumerate(data["stocks"]):
            if old["code"] == stock["code"]:
                data["stocks"][index] = {**old, **stock}
                return
        data["stocks"].append(stock)

    def log(self, collection, item):
        self.read()[collection].append(item)

    def change(self, operation):
        operation(self.read())


def load_store(password):
    sample = not password
    if sample or st.session_state.get("practice_mode"):
        current_store = SessionStore()
    else:
        current_store = Store()
    return sample, current_store, current_store.read()


def stock_label(item):
    code = item.get("code", "")
    suffix = "코드 확인 대기" if code.startswith("pending-") else code
    return f"{item.get('name', '종목')} · {suffix}"


password = os.getenv("APP_PASSWORD", "")
if password and not st.session_state.get("authorized"):
    hero("StockDash", "공식 데이터를 연결해 시장과 기업의 변화를 한 흐름으로 읽습니다.", "SECURE ACCESS")
    left, center, right = st.columns([1, 1.15, 1])
    with center:
        with st.container(border=True):
            st.subheader("개인 대시보드 열기")
            with st.form("login"):
                entered = st.text_input("비밀번호", type="password", placeholder="설정한 비밀번호를 입력하세요")
                if st.form_submit_button("대시보드 열기", type="primary", use_container_width=True):
                    if hmac.compare_digest(entered.encode(), password.encode()):
                        st.session_state.authorized = True
                        st.rerun()
                    st.error("비밀번호를 확인하세요.")
    st.stop()

try:
    sample_mode, store, state = load_store(password)
except Exception:
    hero("저장 공간 연결 확인", "기존 자료는 덮어쓰지 않습니다. 저장소 설정만 확인합니다.", "STORAGE")
    st.error("비밀번호 확인은 통과했지만 종목 저장 공간을 열지 못했습니다.")
    if st.button("저장 연결 없이 임시 실습 시작", type="primary"):
        st.session_state.practice_mode = True
        st.rerun()
    st.stop()


def run_analysis(code):
    try:
        with st.spinner("공식 시세 · 결산 · 가치 · 사업 공시를 확인합니다…"):
            provider = st.session_state.get("directory_provider") or Official()
            if code.startswith("pending-"):
                pending = next((s for s in state["stocks"] if s["code"] == code), {})
                matches = provider.search(pending.get("name", ""))
                if len(matches) != 1:
                    st.session_state.search_candidates = matches
                    st.info("검색 목록에서 정확한 종목을 선택하세요.")
                    return
                code = matches[0]["code"]

            price, price_day, price_name = provider.price(code, date.today())
            try:
                report = provider.automatic(code)
            except DataError as error:
                existing = next((s for s in state["stocks"] if s["code"] == code), {})
                partial = {
                    **existing,
                    "code": code,
                    "name": price_name,
                    "kind": existing.get("kind", "관심"),
                    "price_snapshot": {"price": price, "date": price_day},
                    "analysis_error": str(error),
                }
                st.session_state.latest_analysis = partial
                try:
                    store.save_stock(partial)
                except Exception:
                    pass
                st.session_state.selected_code = code
                st.session_state.nav_choice = "대시보드"
                st.rerun()

            at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
            existing = next((s for s in state["stocks"] if s["code"] == code), {})
            stock = {
                **existing,
                "code": code,
                "name": report["name"],
                "kind": existing.get("kind", "관심"),
                "year": report["years"][-1]["year"],
                "report": report,
                "automatic_brief": brief(report),
                "ai_brief": None,
                "analyzed_at": at,
                "analysis_error": None,
            }
            st.session_state.latest_analysis = stock
            try:
                store.save_stock(stock)
                store.log("journal", {
                    "code": code,
                    "at": at,
                    "kind": "automatic",
                    "report": report,
                    "automatic_brief": stock["automatic_brief"],
                    "ai_brief": None,
                })
            except Exception:
                pass
            st.session_state.selected_code = code
            st.session_state.nav_choice = "대시보드"
        st.rerun()
    except DataError as error:
        st.error(str(error))
    except Exception:
        st.error("분석을 마치지 못했습니다. 이전 결과는 유지됩니다.")


choices = {s["code"]: s for s in state.get("stocks", [])}
latest = st.session_state.get("latest_analysis")
if latest:
    choices[latest["code"]] = latest

NAV_ITEMS = ["대시보드", "내 종목", "계좌 연결", "교육자료", "설정"]
current = st.session_state.get("nav_choice", "대시보드")
if current not in NAV_ITEMS:
    st.session_state.nav_choice = "대시보드"

with st.sidebar:
    brand()
    nav = st.radio("메뉴", NAV_ITEMS, key="nav_choice")
    st.markdown("---")
    if choices:
        codes = list(choices)
        preferred = st.session_state.get("selected_code")
        selected = st.selectbox(
            "현재 종목",
            codes,
            index=codes.index(preferred) if preferred in codes else 0,
            format_func=lambda c: stock_label(choices[c]),
            key="stock_picker",
        )
        stock = choices[selected]
        st.session_state.selected_code = selected
    else:
        stock = {"code": "SAMPLE", "name": "가상 반도체", "report": demo()}

    if sample_mode:
        st.caption("가상 예시 모드")
    elif st.session_state.get("practice_mode"):
        st.caption("임시 저장 모드")
    else:
        st.caption("클라우드 저장" if store.cloud else "실행 서버 저장")

    if password and st.button("로그아웃", use_container_width=True):
        st.session_state.clear()
        st.rerun()

report = stock.get("report")
is_demo = stock.get("code") == "SAMPLE"


def global_search():
    if sample_mode:
        st.info("현재는 가상 예시 모드입니다. APP_PASSWORD와 공식 API 키가 설정되면 실데이터 검색이 열립니다.")
        return
    with st.form("global_search"):
        col_q, col_b = st.columns([6, 1])
        with col_q:
            query = st.text_input(
                "통합 검색",
                placeholder="종목명, 종목코드, 기업명 일부를 검색하세요. 예: 삼성전자 · 005930 · 하이닉스",
                label_visibility="collapsed",
            )
        with col_b:
            submitted = st.form_submit_button("검색·분석", type="primary", use_container_width=True)
    if submitted:
        try:
            provider = st.session_state.get("directory_provider") or Official()
            st.session_state.directory_provider = provider
            matches = provider.search(query)
            st.session_state.search_candidates = matches
            if len(matches) == 1:
                run_analysis(matches[0]["code"])
            elif not matches:
                st.info("일치하는 상장 기업이 없습니다. 기업명 일부나 6자리 종목코드로 다시 검색하세요.")
        except DataError as error:
            st.error(str(error))

    matches = st.session_state.get("search_candidates", [])
    if len(matches) > 1:
        with st.container(border=True):
            with st.form("candidate"):
                candidate = st.selectbox("검색된 종목", matches, format_func=lambda x: x["name"] + " · " + x["code"])
                if st.form_submit_button("이 종목 분석", type="primary"):
                    run_analysis(candidate["code"])


def market_card(title, capability, description):
    caps = active_capabilities()
    if capability in caps:
        card(title, "연결됨", description, "기관 API 데이터 사용 가능")
    else:
        card(title, "data_needed", description, "API 연결 전 · 임의 숫자 미표시")


def render_home():
    hero("나만의 주식 대시보드", "시장 → 투자판단 → 종목 → 실적 → 적정가치 → 브리핑을 한 화면에서 확인합니다.", "PLANX STOCK INTELLIGENCE")
    global_search()

    st.caption("기준: 공식 API·DART 수집 데이터만 표시 · 연결되지 않은 시장/섹터 수치는 data_needed로 표시")

    st.subheader("시장 지수 & 거시")
    mcols = st.columns(5)
    market_specs = [
        ("KOSPI", "market.index", "국내 종합지수"),
        ("KOSDAQ", "market.index", "코스닥 지수"),
        ("USD/KRW", "macro.fx", "원/달러 환율"),
        ("시장 수급", "market.investor_flow", "외국인·기관·개인"),
        ("시장 폭", "market.breadth", "상승·하락 확산도"),
    ]
    for col, spec in zip(mcols, market_specs):
        with col:
            market_card(*spec)

    real_stocks = [item for item in choices.values() if item.get("code") != "SAMPLE"]
    result = brief(report) if report else {}
    v22 = calculate_v22(report) if report else {"status": "data_needed", "reason": "종목 분석 필요"}

    st.subheader("오늘의 투자판단")
    left, middle, right = st.columns([1.05, 1.55, 1.25])
    with left:
        with st.container(border=True):
            total = result.get("total")
            st.metric("종합 투자점수", f"{total:.1f}/100" if isinstance(total, (int, float)) else "data_needed")
            st.caption("성장·수익성·가치 자료가 모두 있을 때만 계산")
            if v22.get("status") == "ok":
                st.caption(f"앵커 품질 {v22['anchor_quality']} · 신뢰도 {v22['confidence']}")
            else:
                st.caption(v22.get("reason", "v2.2 계산 자료 필요"))
    with middle:
        with st.container(border=True):
            st.markdown("#### 핵심 투자 포인트")
            if report:
                st.write(result.get("summary", "공식 데이터 요약 준비 중"))
                st.caption(f"{stock_label(stock)} · {report.get('basis', '확인 필요')}")
            else:
                empty_state("종목 분석 필요", "종목을 검색·분석하면 성장·수익성·가치 근거를 표시합니다.")
    with right:
        with st.container(border=True):
            st.markdown("#### ★ ◆ ▲ 투자 신호")
            if v22.get("status") in ("ok", "reference_only"):
                st.metric("모멘텀", v22.get("momentum_symbol") or "-", f"k {v22.get('k', 0):.2f}배" if v22.get("k") is not None else "data_needed")
                st.write(f"엣지 {v22.get('edge_symbol') or '-'} · 개선 {v22.get('improvement_symbol') or '-'}")
            else:
                st.write("data_needed")
                st.caption(v22.get("reason", "2024·2025 앵커 자료 필요"))

    st.subheader("현재 선택 종목")
    main, side = st.columns([1.8, 1])
    with main:
        with st.container(border=True):
            st.markdown(f"#### {stock.get('name', '선택 종목')}")
            if report and report.get("years"):
                years = pd.DataFrame(report["years"])
                chart = years[["year", "revenue", "profit"]].rename(columns={"year": "연도", "revenue": "매출", "profit": "영업이익"})
                chart["연도"] = chart["연도"].astype(str)
                st.line_chart(chart.set_index("연도")[["매출", "영업이익"]], height=310)
                price = report.get("price")
                c1, c2, c3 = st.columns(3)
                c1.metric("기준 종가", f"{price:,.0f}원" if isinstance(price, (int, float)) else "data_needed")
                c2.metric("매출 성장", f"{result['revenue_growth']:+.1f}%" if result.get("revenue_growth") is not None else "data_needed")
                c3.metric("영업이익률", f"{result['margin']:.1f}%" if result.get("margin") is not None else "data_needed")
            else:
                empty_state("차트 데이터 없음", "공식 종목 분석을 실행하면 결산 실적 추이를 표시합니다.")
    with side:
        with st.container(border=True):
            st.markdown("#### 적정가치")
            if v22.get("fair_price") is not None:
                st.metric("v2.2 적정주가", f"{v22['fair_price']:,.0f}원")
                st.metric("상승여력", f"{v22['upside']:+.1f}%" if v22.get("upside") is not None else "data_needed")
                st.caption(f"{v22['data_basis']} · 앵커 {v22['anchor_quality']}")
            else:
                st.metric("v2.2 적정주가", "data_needed")
                needed = ", ".join(v22.get("data_needed", []))
                st.caption(needed or v22.get("reason", "필요 데이터 확인"))
            if result.get("fair"):
                st.caption(f"기존 역사적 배수 참고: {result['fair']['base']:,.0f}원")

    lower_left, lower_mid, lower_right = st.columns([1.15, 1.15, 1])
    with lower_left:
        with st.container(border=True):
            st.markdown("#### 섹터 & 기업 키워드")
            sectors = result.get("sectors", [])
            if sectors:
                for sector in sectors[:5]:
                    st.write(f"**{sector['sector']}** · " + " · ".join(sector['signals'][:3]))
                st.caption("등락률 데이터는 별도 sector.performance API 연결 전까지 data_needed")
            else:
                st.write("data_needed")
                st.caption("사업보고서 키워드 또는 섹터 데이터 필요")
    with lower_mid:
        with st.container(border=True):
            st.markdown("#### 관심종목")
            if real_stocks:
                rows = []
                for item in real_stocks[:8]:
                    item_report = item.get("report") or {}
                    rows.append({
                        "종목": item.get("name", ""),
                        "구분": item.get("kind", "관심"),
                        "기준가": f"{item_report.get('price'):,.0f}원" if isinstance(item_report.get("price"), (int, float)) else "data_needed",
                        "상태": "분석 완료" if item_report else "분석 필요",
                    })
                st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=245)
            else:
                empty_state("관심종목 없음", "내 종목에서 추가하거나 상단 검색으로 첫 분석을 시작하세요.")
    with lower_right:
        with st.container(border=True):
            st.markdown("#### 최근 공시")
            notices = sorted((report or {}).get("disclosures", []), key=lambda x: x.get("date", ""), reverse=True)
            if notices and not is_demo:
                for item in notices[:5]:
                    st.link_button(f"{item['date']} · {item['title']}", item["url"], use_container_width=True)
            else:
                st.write("data_needed")
                st.caption("선택 종목의 공식 공시 수집 후 표시")

    bottom_left, bottom_right = st.columns([1.2, 1])
    with bottom_left:
        with st.container(border=True):
            st.markdown("#### 실적 추이")
            if report and report.get("years"):
                years = pd.DataFrame(report["years"])
                bars = years[["year", "revenue", "profit"]].rename(columns={"year": "연도", "revenue": "매출", "profit": "영업이익"})
                bars["연도"] = bars["연도"].astype(str)
                st.bar_chart(bars.set_index("연도")[["매출", "영업이익"]], height=260)
                st.caption("단위: 억원 · 수집된 결산 기준")
            else:
                empty_state("data_needed", "결산 실적이 수집되면 연도별 추이를 표시합니다.")
    with bottom_right:
        with st.container(border=True):
            st.markdown("#### AI 브리핑")
            ai = stock.get("ai_brief")
            if ai and ai.get("status") == "ok":
                st.write(ai.get("text", ""))
                st.caption("공식 데이터 기반 AI 해설 · 원문 대조 필요")
            elif report:
                st.write(result.get("summary", "자동 브리핑 자료 부족"))
                st.caption("현재는 LLM API 호출 없이 공식 데이터 자동 요약을 표시합니다.")
            else:
                empty_state("data_needed", "종목 분석 후 공식 데이터 기반 브리핑을 표시합니다.")


def render_stock_detail():
    hero(stock_label(stock), "기업 특징 → 실적 → 가치 → 공시 순서로 확인합니다.", "STOCK 360")
    global_search()
    if not report:
        empty_state("기업·재무 자료 없음", "대시보드에서 종목을 검색·분석하면 상세 화면을 표시합니다.")
        return
    result = brief(report)
    v22 = calculate_v22(report)
    cols = st.columns(4)
    cols[0].metric("기준 종가", f"{report['price']:,.0f}원" if isinstance(report.get("price"), (int, float)) else "data_needed")
    cols[1].metric("성장", result.get("growth", "data_needed"))
    cols[2].metric("가치 상태", result.get("value", "data_needed"))
    cols[3].metric("v2.2 앵커", v22.get("anchor_quality", "data_needed"))
    st.write(result.get("summary", ""))
    years = pd.DataFrame(report.get("years", []))
    if not years.empty:
        st.bar_chart(years.set_index("year")[["revenue", "profit"]])
        st.dataframe(years, hide_index=True, use_container_width=True)
    notices = sorted(report.get("disclosures", []), key=lambda x: x.get("date", ""), reverse=True)
    if notices and not is_demo:
        st.subheader("최근 공시")
        for item in notices[:12]:
            st.link_button(f"{item['date']} · {item['title']}", item["url"], use_container_width=True)


def render_settings():
    hero("설정과 데이터 연결", "기관 API의 인증·응답·사용 가능 기능을 확인합니다.", "SETTINGS")
    st.caption("키 값 자체는 화면에 표시하지 않습니다.")
    if st.button("전체 연결 진단", type="primary"):
        with st.spinner("기관 API 상태를 확인합니다…"):
            st.session_state.provider_health = health_all()
    health_by_id = {row["provider_id"]: row for row in st.session_state.get("provider_health", [])}
    for spec in PROVIDERS:
        check = health_by_id.get(spec.provider_id)
        with st.container(border=True):
            left, right = st.columns([2, 5])
            with left:
                st.subheader(spec.name)
                source_badge("정상" if check and check["status"] == "ok" else "인증정보 필요" if check and check["status"] == "not_configured" else "진단 전", "ok" if check and check["status"] == "ok" else "wait")
            with right:
                st.write(" · ".join(spec.capabilities))
                if check:
                    st.caption(f"{check['detail']} · 응답 {check['latency_ms']}ms · 확인 {check['checked_at']}")


if nav == "대시보드":
    render_home()
elif nav == "내 종목":
    tabs = st.tabs(["조사 요청", "상세 분석"])
    with tabs[0]:
        render_research(store, state, sample_mode)
    with tabs[1]:
        render_stock_detail()
elif nav == "계좌 연결":
    render_portfolio(store, sample_mode)
elif nav == "교육자료":
    render_education()
else:
    render_settings()
