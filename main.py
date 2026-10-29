import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 주거 공간 가구 배치 진단기", page_icon="🏠", layout="centered")

st.title("🏠 AI 기반 3D 주거 공간 배치 & 쾌적도 진단기")
st.caption("국제 건축 표준 단위(m, m², m³)와 가로·세로·높이 3차원 치수를 바탕으로 **3D 가구 배치 도면** 및 **공간 쾌적도**를 실시간 진단합니다.")

st.divider()

# -------------------------------------------------------------
# 2. 3D 입체 도형(Mesh3D) 생성 함수
# -------------------------------------------------------------
def create_3d_box(x0, y0, z0, dx, dy, dz, color, name):
    """Plotly 3D 렌더링을 위한 직육면체 가구 객체 생성"""
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    mesh = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=0.85,
        name=name,
        showscale=False,
        flatshading=True,
        hoverinfo="name"
    )
    return mesh

# -------------------------------------------------------------
# 3. 메인 프로그램
# -------------------------------------------------------------
try:
    # [입력 1] 방 치수 입력 (가로, 세로, 천장 높이)
    st.subheader("1. 방 공간 치수 입력 (단위: m)")
    col_w, col_l, col_h = st.columns(3)

    with col_w:
        room_w = st.number_input("방 가로 길이 (m):", min_value=0.0, max_value=20.0, value=3.5, step=0.1)
    with col_l:
        room_l = st.number_input("방 세로 길이 (m):", min_value=0.0, max_value=20.0, value=3.0, step=0.1)
    with col_h:
        room_h = st.number_input("천장 높이 (m):", min_value=1.5, max_value=5.0, value=2.4, step=0.1)

    # 예외 처리: 0 이하 치수 차단
    if room_w <= 0 or room_l <= 0 or room_h <= 0:
        st.warning("⚠️ 방의 가로, 세로, 천장 높이는 모두 0보다 큰 수치이어야 합니다.")
        st.stop()

    room_area = room_w * room_l
    room_vol = room_w * room_l * room_h
    st.info(f"📏 입력한 방 공간 정보: 바닥 면적 **{room_area:.2f} m²** | 전체 체적(부피) **{room_vol:.2f} m³**")

    st.divider()

    # [입력 2] 가구 선택 및 세부 치수 입력 (가로, 세로, 높이)
    st.subheader("2. 배치할 가구 선택 및 3D 치수 설정 (단위: m)")

    DEFAULT_FURNITURE = {
        "싱글 침대": {"w": 1.0, "l": 2.0, "h": 0.5, "color": "#4A90E2"},
        "퀸 침대": {"w": 1.5, "l": 2.0, "h": 0.5, "color": "#357ABD"},
        "1인용 책상": {"w": 1.2, "l": 0.7, "h": 0.75, "color": "#50E3C2"},
        "옷장/장롱": {"w": 1.2, "l": 0.6, "h": 2.0, "color": "#F5A623"},
        "2인용 소파": {"w": 1.5, "l": 0.8, "h": 0.8, "color": "#B8E986"},
        "서랍장/협탁": {"w": 0.6, "l": 0.5, "h": 0.7, "color": "#BD10E0"}
    }

    selected_preset = st.multiselect(
        "배치할 가구 항목을 선택하세요:",
        options=list(DEFAULT_FURNITURE.keys()),
        default=["싱글 침대", "1인용 책상", "옷장/장롱"]
    )

    total_furn_area = 0.0
    total_furn_vol = 0.0
    max_furn_h = 0.0
    furniture_list = []

    if selected_preset:
        st.markdown("##### ✏️ 선택 가구별 3D 규격(가로x세로x높이) 및 수량 조정")
        for idx, item in enumerate(selected_preset):
            preset = DEFAULT_FURNITURE[item]

            f_col1, f_col2, f
