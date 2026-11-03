import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 복층 정밀 건축 & 개조 시스템", page_icon="🏛️", layout="wide")

st.title("🏛️ AI 기반 3D 정밀 건축 평면도 & 디테일 가구 / 커스텀 개조 시스템")
st.caption("현관 중문, 디테일 디자이너 가구(액자/러그/쿠션/거울), **3D 벽 높이 조절 및 커스텀 문/창문 개조 기능**을 탑재했습니다.")

st.divider()

# -------------------------------------------------------------
# 2. 3D 메쉬 생성 및 디테일 가구 헬퍼 함수
# -------------------------------------------------------------
def create_3d_box(x0, y0, z0, dx, dy, dz, color, name, opacity=0.85):
    """Plotly 3D 직육면체 객체 생성"""
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    return go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k,
        color=color, opacity=opacity, name=name,
        showscale=False, flatshading=True, hoverinfo="name"
    )

def create_stairs(x0, y0, z0, dx, dy, dz, num_steps=10, color="#8D6E63", name="연결 계단"):
    traces = []
    step_h = dz / num_steps
    step_l = dy / num_steps
    for step in range(num_steps):
        sz0 = z0 + step * step_h
        sy0 = y0 + step * step_l
        traces.append(create_3d_box(x0, sy0, sz0, dx, step_l, step_h, color, f"{name} ({step+1}단)"))
    return traces

# -------------------------------------------------------------
# 3. 메인 프로그램 실행
# -------------------------------------------------------------
try:
    # [입력 1] 전체 집 치수 및 건축 개조 옵션
    st.subheader("1. 집 전체 치수 및 커스텀 건축 개조 (벽/문/창문)")
    
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        house_w = st.number_input("집 전체 가로 (m):", min_value=5.0, max_value=100.0, value=10.0, step=0.5)
    with c2:
        house_l = st.number_input("집 전체 세로 (m):", min_value=5.0, max_value=100.0, value=8.0, step=0.5)
    with c3:
        house_h = st.slider("📐 3D 벽체 높이 수동 조절 (m):", min_value=1.0, max_value=6.0, value=2.5, step=0.1)
    with c4:
        st.write("**건축 옵션**")
        use_2nd_floor = st.checkbox("🏢 2층(복층) 구조 활성화", value=False)
        show_front_door = st.checkbox("🚪 현관 중문/출입문 닫힘 표시", value=True)

    num_floors = 2 if use_2nd_floor else 1
    total_house_area = house_w * house_l * num_floors
    pyeong = total_house_area / 3.3058
    total_render_height = house_h * num_floors  # 오류 보완 변수 선언

    st.info(f"🏡 전체 주택 연면적: **{total_house_area:.2f} m²** (약 {pyeong:.1f}평) | 벽 높이: **{house_h:.1f}m** | 층수: **{num_floors}층** | 총 높이: **{total_render_height:.1f}m**")

    # -------------------------------------------------------------
    # AI 자동 방 구획 분할 (1층 & 2층)
    # -------------------------------------------------------------
    wall_th = 0.15
    door_w = 0.9
    win_h_start = 0.9
    win_h = 1.2
