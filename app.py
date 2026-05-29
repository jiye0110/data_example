import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="대학 연구 지표 대시보드",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background-color: #F5F7FA; }
[data-testid="stSidebar"] { background-color: #0D2B5E; }
[data-testid="stSidebar"] * { color: #E8EDF5 !important; }
[data-testid="metric-container"] {
    background: white; border: 1px solid #E4E9F2;
    border-radius: 12px; padding: 16px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important; color: #0D2B5E !important; font-weight: 600;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important; color: #6B7A99 !important;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;
}
.page-title { font-size: 22px; font-weight: 700; color: #0D2B5E; margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: #6B7A99; margin-bottom: 24px; }
.section-header {
    font-size: 11px; font-weight: 700; color: #6B7A99;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 28px 0 12px; padding-bottom: 8px; border-bottom: 1px solid #E4E9F2;
}
.highlight-box {
    background: #EEF4FF; border-left: 4px solid #0D2B5E;
    border-radius: 0 10px 10px 0; padding: 12px 18px;
    font-size: 13px; color: #1E3A8A; margin-top: 10px; line-height: 1.7;
}
.warn-box {
    background: #FFF7ED; border-left: 4px solid #F97316;
    border-radius: 0 10px 10px 0; padding: 12px 18px;
    font-size: 13px; color: #9A3412; margin-top: 10px; line-height: 1.7;
}
.good-box {
    background: #F0FDF4; border-left: 4px solid #16A34A;
    border-radius: 0 10px 10px 0; padding: 12px 18px;
    font-size: 13px; color: #166534; margin-top: 10px; line-height: 1.7;
}
.footnote {
    font-size: 11px; color: #9AA3B2; margin-top: 24px;
    padding-top: 12px; border-top: 1px solid #E4E9F2;
}
</style>
""", unsafe_allow_html=True)

# ── 설정 ──────────────────────────────────────────────
HIGHLIGHT_UNIV = "명지대"
HIGHLIGHT_COLOR = "#E8392A"
BASE_COLOR = "#93B8E0"
DATA_FILE = "data_example.xlsx"

LAYOUT = dict(
    font=dict(family="Noto Sans KR, sans-serif", size=12, color="#2D3748"),
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=20, r=20, t=40, b=20),
    hoverlabel=dict(bgcolor="white", font_size=12)
)

# ── 데이터 로드 ───────────────────────────────────────
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df['대학명'] = df['대학명'].astype(str).str.strip()
    for col in ['Publications', 'Citations', 'FWCI']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.sort_values('FWCI', ascending=False).reset_index(drop=True)
    df['FWCI_순위'] = df.index + 1
    df['is_highlight'] = df['대학명'].eq(HIGHLIGHT_UNIV)
    return df

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
if not os.path.exists(data_path):
    st.error(f"❌ 데이터 파일을 찾을 수 없습니다: {DATA_FILE}")
    st.stop()

df = load_data(data_path)
total = len(df)
my_row = df[df['대학명'] == HIGHLIGHT_UNIV].iloc[0]

# ── 사이드바 ──────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 🎓 {HIGHLIGHT_UNIV}\n**대학 연구 지표 대시보드**", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "페이지",
        ["📋 데이터 개요", "📊 전체 대학 순위", "🔍 심층 분석", "🏫 우리 대학 프로파일"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:#93A8D4;'>📂 {DATA_FILE}<br>대상: {total}개교</div>",
        unsafe_allow_html=True
    )

# ────────────────────────────────────────────────────
# 페이지 1: 데이터 개요
# ────────────────────────────────────────────────────
if page == "📋 데이터 개요":
    st.markdown("<div class='page-title'>데이터 개요</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>분석 대상 지표 및 데이터 구조 설명</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 대학 수", f"{total}개교")
    c2.metric("평균 Publications", f"{df['Publications'].mean():,.0f}")
    c3.metric("평균 Citations", f"{df['Citations'].mean():,.0f}")
    c4.metric("평균 FWCI", f"{df['FWCI'].mean():.3f}")

    st.markdown("<div class='section-header'>지표 설명</div>", unsafe_allow_html=True)
    desc_df = pd.DataFrame([
        {"지표명": "Publications", "설명": "분석 기간 내 국제학술지 등재 논문 수"},
        {"지표명": "Citations", "설명": "해당 논문들이 받은 총 피인용 횟수"},
        {"지표명": "FWCI", "설명": "Field-Weighted Citation Impact. 전 세계 동일 분야·연도 평균 대비 피인용 비율. 1.0 = 세계 평균"},
    ])
    st.dataframe(desc_df, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-header'>원본 데이터 (상위 20개교)</div>", unsafe_allow_html=True)
    display_df = df[['FWCI_순위', '대학명', 'Publications', 'Citations', 'FWCI']].head(20).copy()
    display_df.columns = ['FWCI 순위', '대학명', 'Publications', 'Citations', 'FWCI']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────
# 페이지 2: 전체 대학 순위
# ────────────────────────────────────────────────────
elif page == "📊 전체 대학 순위":
    st.markdown("<div class='page-title'>전체 대학 순위</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>FWCI 기준 전체 순위 비교</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["FWCI 순위", "Publications 순위", "Citations 순위"])

    def make_hbar(sort_col, label):
        sorted_df = df.sort_values(sort_col, ascending=False).reset_index(drop=True)
        sorted_df['순위'] = sorted_df.index + 1
        colors = [HIGHLIGHT_COLOR if v else BASE_COLOR for v in sorted_df['is_highlight']]
        fig = go.Figure(go.Bar(
            y=sorted_df['대학명'], x=sorted_df[sort_col],
            orientation='h',
            marker_color=colors,
            hovertemplate='<b>%{y}</b><br>' + label + ': %{x:,.4f}<extra></extra>'
        ))
        avg_val = sorted_df[sort_col].mean()
        fig.add_vline(x=avg_val, line_dash='dash', line_color='#718096',
                      annotation_text=f'전체 평균({avg_val:,.3f})',
                      annotation_font=dict(size=10, color='#718096'))
        fig.update_layout(
            **LAYOUT,
            height=min(max(500, total * 22), 1400),
            yaxis=dict(autorange='reversed', tickfont=dict(size=10)),
            xaxis=dict(title=label, gridcolor='#F0F0F0')
        )
        return fig

    with tab1:
        st.plotly_chart(make_hbar('FWCI', 'FWCI'), use_container_width=True)
    with tab2:
        st.plotly_chart(make_hbar('Publications', 'Publications'), use_container_width=True)
    with tab3:
        st.plotly_chart(make_hbar('Citations', 'Citations'), use_container_width=True)

# ────────────────────────────────────────────────────
# 페이지 3: 심층 분석
# ────────────────────────────────────────────────────
elif page == "🔍 심층 분석":
    st.markdown("<div class='page-title'>심층 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>지표 간 관계 및 분포 분석</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Publications vs FWCI 산점도</div>", unsafe_allow_html=True)
    fig_scatter = go.Figure()
    normal = df[~df['is_highlight']]
    highlight = df[df['is_highlight']]

    fig_scatter.add_trace(go.Scatter(
        x=normal['Publications'], y=normal['FWCI'],
        mode='markers+text',
        text=normal['대학명'],
        textposition='top center',
        textfont=dict(size=9),
        marker=dict(color=BASE_COLOR, size=8, opacity=0.7),
        hovertemplate='<b>%{text}</b><br>Publications: %{x:,}<br>FWCI: %{y:.3f}<extra></extra>',
        name='기타 대학'
    ))
    fig_scatter.add_trace(go.Scatter(
        x=highlight['Publications'], y=highlight['FWCI'],
        mode='markers+text',
        text=highlight['대학명'],
        textposition='top center',
        textfont=dict(size=11, color=HIGHLIGHT_COLOR),
        marker=dict(color=HIGHLIGHT_COLOR, size=14),
        hovertemplate='<b>%{text}</b><br>Publications: %{x:,}<br>FWCI: %{y:.3f}<extra></extra>',
        name=HIGHLIGHT_UNIV
    ))
    avg_pub = df['Publications'].mean()
    avg_fwci = df['FWCI'].mean()
    fig_scatter.add_hline(y=avg_fwci, line_dash='dash', line_color='#CBD5E1',
                          annotation_text=f'FWCI 평균({avg_fwci:.3f})',
                          annotation_font=dict(size=10, color='#718096'))
    fig_scatter.add_vline(x=avg_pub, line_dash='dash', line_color='#CBD5E1',
                          annotation_text=f'Publications 평균({avg_pub:,.0f})',
                          annotation_font=dict(size=10, color='#718096'))
    fig_scatter.update_layout(
        **LAYOUT, height=550,
        xaxis=dict(title='Publications', gridcolor='#F0F0F0', tickformat=','),
        yaxis=dict(title='FWCI', gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("<div class='section-header'>FWCI 분포 히스토그램</div>", unsafe_allow_html=True)
    fig_hist = px.histogram(df, x='FWCI', nbins=15, color_discrete_sequence=[BASE_COLOR])
    fig_hist.add_vline(x=float(my_row['FWCI']), line_color=HIGHLIGHT_COLOR, line_width=2,
                       annotation_text=f'{HIGHLIGHT_UNIV} ({float(my_row["FWCI"]):.3f})',
                       annotation_font=dict(color=HIGHLIGHT_COLOR, size=11))
    fig_hist.add_vline(x=avg_fwci, line_dash='dash', line_color='#718096',
                       annotation_text=f'전체 평균({avg_fwci:.3f})',
                       annotation_font=dict(size=10, color='#718096'))
    fig_hist.update_layout(**LAYOUT, height=350,
                           xaxis=dict(title='FWCI', gridcolor='#F0F0F0'),
                           yaxis=dict(title='대학 수', gridcolor='#F0F0F0'))
    st.plotly_chart(fig_hist, use_container_width=True)

# ────────────────────────────────────────────────────
# 페이지 4: 우리 대학 프로파일
# ────────────────────────────────────────────────────
else:
    st.markdown(f"<div class='page-title'>{HIGHLIGHT_UNIV} 프로파일</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>3개 지표 종합 현황</div>", unsafe_allow_html=True)

    fwci_rank = int(my_row['FWCI_순위'])
    pub_rank = int(df.sort_values('Publications', ascending=False).reset_index(drop=True)
                   [df.sort_values('Publications', ascending=False).reset_index(drop=True)['대학명'] == HIGHLIGHT_UNIV].index[0]) + 1
    cit_rank = int(df.sort_values('Citations', ascending=False).reset_index(drop=True)
                   [df.sort_values('Citations', ascending=False).reset_index(drop=True)['대학명'] == HIGHLIGHT_UNIV].index[0]) + 1

    c1, c2, c3 = st.columns(3)
    c1.metric("FWCI 순위", f"{fwci_rank}위 / {total}개교", f"상위 {fwci_rank/total*100:.1f}%")
    c2.metric("Publications 순위", f"{pub_rank}위 / {total}개교", f"상위 {pub_rank/total*100:.1f}%")
    c3.metric("Citations 순위", f"{cit_rank}위 / {total}개교", f"상위 {cit_rank/total*100:.1f}%")

    # 레이더 차트
    def pct_score(rank, total):
        return (1 - (rank - 1) / total) * 100

    r = [pct_score(fwci_rank, total), pct_score(pub_rank, total), pct_score(cit_rank, total)]
    categories = ['FWCI', 'Publications', 'Citations']

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=r + [r[0]], theta=categories + [categories[0]],
        fill='toself', name=HIGHLIGHT_UNIV,
        line_color=HIGHLIGHT_COLOR, fillcolor='rgba(232,57,42,0.15)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[50, 50, 50, 50], theta=categories + [categories[0]],
        name='중위 기준(50%)',
        line=dict(color=BASE_COLOR, dash='dash')
    ))
    fig_radar.update_layout(
        **LAYOUT, height=420,
        polar=dict(radialaxis=dict(range=[0, 100], ticksuffix='%')),
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # 상위 20개교 비교
    st.markdown("<div class='section-header'>상위 20개교 FWCI 비교</div>", unsafe_allow_html=True)
    top20 = df.head(20).copy()
    if not top20['is_highlight'].any():
        top20 = pd.concat([top20, df[df['is_highlight']]]).reset_index(drop=True)
    top20 = top20.sort_values('FWCI', ascending=False)
    colors = [HIGHLIGHT_COLOR if v else BASE_COLOR for v in top20['is_highlight']]
    fig_top = go.Figure(go.Bar(
        x=top20['대학명'], y=top20['FWCI'],
        marker_color=colors,
        hovertemplate='<b>%{x}</b><br>FWCI: %{y:.4f}<extra></extra>'
    ))
    fig_top.add_hline(y=avg_fwci, line_dash='dash', line_color='#718096',
                      annotation_text=f'전체 평균({avg_fwci:.3f})',
                      annotation_font=dict(size=10))
    fig_top.update_layout(
        **LAYOUT, height=380,
        xaxis=dict(tickangle=-35, tickfont=dict(size=10)),
        yaxis=dict(title='FWCI', gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig_top, use_container_width=True)

    # 요약 테이블
    summary = pd.DataFrame([
        {'지표': 'FWCI', '값': f"{float(my_row['FWCI']):.4f}", '전체 평균': f"{df['FWCI'].mean():.4f}", '순위': f"{fwci_rank}위 / {total}개교"},
        {'지표': 'Publications', '값': f"{int(my_row['Publications']):,}", '전체 평균': f"{df['Publications'].mean():,.0f}", '순위': f"{pub_rank}위 / {total}개교"},
        {'지표': 'Citations', '값': f"{int(my_row['Citations']):,}", '전체 평균': f"{df['Citations'].mean():,.0f}", '순위': f"{cit_rank}위 / {total}개교"},
    ])
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.download_button(
        '요약표 CSV 다운로드',
        summary.to_csv(index=False).encode('utf-8-sig'),
        f'{HIGHLIGHT_UNIV}_research_summary.csv',
        'text/csv'
    )
    st.markdown("<div class='footnote'>점수 = 백분위 순위 기준 (100점 = 1위, 50점 = 중위)</div>", unsafe_allow_html=True)
