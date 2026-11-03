import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 복층 정밀 건축 & 스마트 가구 배치", page_icon="🏛️", layout="wide")

st.title("🏛️ AI 기반 3D 정밀 건축 평면도 & 스마트 가구 배치 / 커스텀 개조 시스템")
st.caption("AI 생활 밀착형 자동 가구 배치, **3D 가구 실시간 좌표 이동**, 깔끔한 시각화 및 **외벽/문/창문 커스텀 개조** 기능을 제공합니다.")

st.divider()

# -------------------------------------------------------------
# 2. 3D 메쉬 생성 및 건축 헬퍼 함수
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
    st.subheader("1. 외벽 치수 확장 및 건축 개조 옵션")
    
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        house_w = st.number_input("📏 집 전체 가로 폭 (m):", min_value=5.0, max_value=100.0, value=10.0, step=0.5)
    with c2:
        house_l = st.number_input("📐 집 전체 세로 길이 (m):", min_value=5.0, max_value=100.0, value=8.0, step=0.5)
    with c3:
        house_h = st.slider("🧱 3D 벽체 높이 조절 (m):", min_value=1.0, max_value=6.0, value=2.5, step=0.1)
    with c4:
        st.write("**건축 옵션**")
        use_2nd_floor = st.checkbox("🏢 2층(복층) 구조 활성화", value=False)
        show_front_door = st.checkbox("🚪 메인 현관 출입문 표시", value=True)

    num_floors = 2 if use_2nd_floor else 1
    total_house_area = house_w * house_l * num_floors
    pyeong = total_house_area / 3.3058
    total_render_height = house_h * num_floors

    st.info(f"🏡 전체 주택 연면적: **{total_house_area:.2f} m²** (약 {pyeong:.1f}평) | 벽 높이: **{house_h:.1f}m** | 층수: **{num_floors}층**")

    # -------------------------------------------------------------
    # AI 자동 방 구획 분할
    # -------------------------------------------------------------
    wall_th = 0.15
    door_w = 0.9
    win_h_start = 0.9
    win_h = 1.2

    y_mid = house_l * 0.55
    x_mid1 = house_w * 0.5
    x_mid2 = house_w * 0.38
    x_mid3 = house_w * 0.75
    y_bath = house_l * 0.80

    rooms_1f = {
        "[1층] 거실 (Living Room)": {"x0": 0, "y0": 0, "w": x_mid1, "l": y_mid, "color": "#FAFAFA", "z": 0},
        "[1층] 안방 (Master Bedroom)": {"x0": x_mid1, "y0": 0, "w": house_w - x_mid1, "l": y_mid, "color": "#F3E5F5", "z": 0},
        "[1층] 작은방 (Bedroom 2)": {"x0": 0, "y0": y_mid, "w": x_mid2, "l": house_l - y_mid, "color": "#E1F5FE", "z": 0},
        "[1층] 주방/식당 (Kitchen)": {"x0": x_mid2, "y0": y_mid, "w": x_mid3 - x_mid2, "l": house_l - y_mid, "color": "#FFF3E0", "z": 0},
        "[1층] 욕실/화장실 (Bathroom)": {"x0": x_mid3, "y0": y_mid, "w": house_w - x_mid3, "l": y_bath - y_mid, "color": "#E0F7FA", "z": 0},
        "[1층] 현관 (Entrance)": {"x0": x_mid3, "y0": y_bath, "w": house_w - x_mid3, "l": house_l - y_bath, "color": "#E8EAF6", "z": 0}
    }

    rooms_2f = {}
    if use_2nd_floor:
        rooms_2f = {
            "[2층] 메인 서재/작업실 (Study)": {"x0": 0, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#EFEBE9", "z": house_h},
            "[2층] 게스트 룸 (Guest Room)": {"x0": house_w * 0.5, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#F1F8E9", "z": house_h},
            "[2층] 취미실/드레스룸 (Hobby Room)": {"x0": 0, "y0": house_l * 0.55, "w": house_w * 0.45, "l": house_l * 0.45, "color": "#FFF8E1", "z": house_h},
            "[2층] 2층 테라스/욕실 (Terrace & Bath)": {"x0": house_w * 0.45, "y0": house_l * 0.55, "w": house_w * 0.55, "l": house_l * 0.45, "color": "#E0F2F1", "z": house_h}
        }

    all_rooms = {**rooms_1f, **rooms_2f}

    # -------------------------------------------------------------
    # [3D 자유 개조 옵션] 외벽 길이 및 문/창문 수동 개조
    # -------------------------------------------------------------
    st.divider()
    with st.expander("🛠️ 3D 건축 수동 개조 (문/창문/벽체 위치 지정 추가)", expanded=False):
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            m_type = st.selectbox("개조 종류:", options=["창문 (Window)", "방문/출입문 (Door)", "벽체 파티션 (Wall)"])
            m_room = st.selectbox("설치할 방 선택:", options=list(all_rooms.keys()))
        with col_m2:
            m_wall_pos = st.selectbox("벽면 방향:", options=["전면(남측)", "후면(북측)", "좌측(서측)", "우측(동측)"])
            m_offset = st.number_input("벽 시작점에서 거리 Offset (m):", min_value=0.0, max_value=20.0, value=1.0, step=0.2)
        with col_m3:
            m_w = st.number_input("가로 폭 (m):", min_value=0.3, max_value=5.0, value=1.2, step=0.1)
            m_h = st.number_input("높이 (m):", min_value=0.5, max_value=3.0, value=1.2, step=0.1)
        with col_m4:
            m_z = st.number_input("바닥 높이 Z (m):", min_value=0.0, max_value=4.0, value=0.9, step=0.1)
            if st.button("🔨 커스텀 구조물 추가"):
                if "custom_structures" not in st.session_state:
                    st.session_state.custom_structures = []
                st.session_state.custom_structures.append({
                    "type": m_type, "room": m_room, "wall": m_wall_pos,
                    "offset": m_offset, "w": m_w, "h": m_h, "z": m_z
                })
                st.success("새 개조 건축 요소가 추가되었습니다!")
                st.rerun()

        if "custom_structures" in st.session_state and st.session_state.custom_structures:
            st.markdown("##### 🛠️ 현재 추가된 커스텀 개조 구조물")
            for cs_idx, cs in enumerate(st.session_state.custom_structures):
                cs_col1, cs_col2 = st.columns([4, 1])
                cs_col1.write(f"• **[{cs['room']}]** {cs['wall']} (거리 {cs['offset']}m) - {cs['type']} (폭:{cs['w']}m, 높이:{cs['h']}m)")
                if cs_col2.button("삭제", key=f"del_cs_{cs_idx}"):
                    st.session_state.custom_structures.pop(cs_idx)
                    st.rerun()

    st.divider()

    # -------------------------------------------------------------
    # [입력 2] AI 기반 인간공학적 스마트 기본 가구 세팅
    # -------------------------------------------------------------
    st.subheader("2. 가구 스마트 자동 배치 & 3D 위치 수동 이동 조절")

    # 기본 가구 초기화
    if "custom_items" not in st.session_state:
        st.session_state.custom_items = [
            # [현관] 동선 비워둠 (입구 문 바로 앞X, 벽면 부착)
            {"name": "🚪 현관 슬라이딩 중문", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.1, "rel_y": 0.05, "w": 0.9, "l": 0.1, "h": 2.1, "color": "#3E2723"},
            {"name": "신발장 및 전신거울", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.2, "rel_y": 0.4, "w": 1.0, "l": 0.35, "h": 1.4, "color": "#795548"},
            {"name": "현관 바닥 매트", "room": "[1층] 현관 (Entrance)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "rel_x": 0.3, "rel_y": 0.9, "w": 0.8, "l": 0.5, "h": 0.02, "color": "#B0BEC5"},

            # [거실] 인간공학적 배치 (소파 벽면, 소파테이블 중앙, TV장 맞은편 벽, TV는 TV장 위 정확 부착)
            {"name": "샤기 거실 패턴 러그", "room": "[1층] 거실 (Living Room)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "rel_x": 0.8, "rel_y": 1.2, "w": 2.4, "l": 1.8, "h": 0.02, "color": "#FFE082"},
            {"name": "4인용 패브릭 소파", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.3, "rel_y": 0.5, "w": 2.4, "l": 0.9, "h": 0.85, "color": "#5C6BC0"},
            {"name": "소파 인테리어 쿠션", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "4인용 패브릭 소파", "rel_x": 0.2, "rel_y": 0.2, "w": 0.5, "l": 0.4, "h": 0.25, "color": "#FF8A65"},
            {"name": "원목 소파 테이블", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.9, "rel_y": 1.7, "w": 1.1, "l": 0.6, "h": 0.4, "color": "#8D6E63"},
            {"name": "대형 거실 TV장", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.5, "rel_y": 3.7, "w": 2.0, "l": 0.4, "h": 0.5, "color": "#4E342E"},
            {"name": "75인치 스마트 TV", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "대형 거실 TV장", "rel_x": 0.2, "rel_y": 0.1, "w": 1.6, "l": 0.15, "h": 0.9, "color": "#1A237E"},
            {"name": "🖼️ 대형 갤러리 벽걸이 액자", "room": "[1층] 거실 (Living Room)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "rel_x": 0.8, "rel_y": 0.05, "w": 1.5, "l": 0.08, "h": 0.9, "color": "#FFB300"},

            # [안방] 침대 헤드 벽면, 협탁 옆, 붙박이장 측면
            {"name": "침실 원형 카페트", "room": "[1층] 안방 (Master Bedroom)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "rel_x": 0.5, "rel_y": 1.2, "w": 1.8, "l": 1.8, "h": 0.02, "color": "#CE93D8"},
            {"name": "퀸 사이즈 침대", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.4, "rel_y": 0.5, "w": 1.6, "l": 2.1, "h": 0.55, "color": "#3949AB"},
            {"name": "원목 침대 협탁", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 2.1, "rel_y": 0.5, "w": 0.5, "l": 0.4, "h": 0.5, "color": "#A1887F"},
            {"name": "무드 스탠드 조명", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "원목 침대 협탁", "rel_x": 0.12, "rel_y": 0.08, "w": 0.25, "l": 0.25, "h": 0.4, "color": "#FFF176"},
            {"name": "안방 대형 붙박이장", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 2.8, "rel_y": 0.5, "w": 1.8, "l": 0.65, "h": 2.1, "color": "#6D4C41"},
            {"name": "🖼️ 안방 인테리어 유화 액자", "room": "[1층] 안방 (Master Bedroom)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "rel_x": 0.7, "rel_y": 0.05, "w": 1.0, "l": 0.08, "h": 0.7, "color": "#BA68C8"},

            # [작은방]
            {"name": "슈퍼싱글 침대", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.3, "rel_y": 0.4, "w": 1.1, "l": 2.0, "h": 0.5, "color": "#0288D1"},
            {"name": "1인용 집중 스터디 책상", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 1.6, "rel_y": 0.4, "w": 1.2, "l": 0.7, "h": 0.75, "color": "#26A69A"},
            {"name": "데스크탑 32인치 모니터", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "1인용 집중 스터디 책상", "rel_x": 0.3, "rel_y": 0.2, "w": 0.6, "l": 0.2, "h": 0.45, "color": "#212121"},
            {"name": "🖼️ 벽걸이 책선반", "room": "[1층] 작은방 (Bedroom 2)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "rel_x": 1.6, "rel_y": 0.05, "w": 1.2, "l": 0.15, "h": 0.3, "color": "#8D6E63"},

            # [주방/식당]
            {"name": "4인용 아일랜드 식탁", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.5, "rel_y": 1.0, "w": 1.4, "l": 0.8, "h": 0.75, "color": "#66BB6A"},
            {"name": "양문형 대형 비스포크 냉장고", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 2.3, "rel_y": 1.8, "w": 0.95, "l": 0.9, "h": 1.85, "color": "#78909C"},
            {"name": "🖼️ 주방 벽걸이 와인 수납장", "room": "[1층] 주방/식당 (Kitchen)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "rel_x": 0.5, "rel_y": 0.05, "w": 1.0, "l": 0.2, "h": 0.5, "color": "#5D4037"},

            # [욕실/화장실]
            {"name": "양변기 & 세면대 세트", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 0.2, "rel_y": 0.2, "w": 0.9, "l": 0.6, "h": 0.8, "color": "#00BCD4"},
            {"name": "유리 샤워부스/욕조", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "rel_x": 1.3, "rel_y": 0.2, "w": 0.9, "l": 0.9, "h": 1.9, "color": "#4DD0E1"},
            {"name": "🖼️ 욕실 슬라이딩 거울 수납장", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "rel_x": 0.2, "rel_y": 0.05, "w": 0.8, "l": 0.15, "h": 0.6, "color": "#B2EBF2"}
        ]

    # 세션 방 이름 보정
    for item in st.session_state.custom_items:
        if not (item["room"].startswith("[1층]") or item["room"].startswith("[2층]")):
            item["room"] = f"[1층] {item['room']}"

    # -------------------------------------------------------------
    # 🛋️ 가구 수동 위치 (X, Y) 세부 조절 인터페이스
    # -------------------------------------------------------------
    with st.expander("🛋️ 가구 3D 수동 위치 조절 (원하는 가구 선택 후 X, Y 좌표 이동)", expanded=False):
        valid_item_names = [item["name"] for item in st.session_state.custom_items if item["base_item"] == "바닥 (z=0)"]
        if valid_item_names:
            sel_item_name = st.selectbox("🎯 이동할 가구 선택:", options=valid_item_names)
            target_item = next((item for item in st.session_state.custom_items if item["name"] == sel_item_name), None)
            
            if target_item:
                t_room = all_rooms[target_item["room"]]
                max_x_offset = max(0.1, t_room["w"] - target_item["w"] - 0.1)
                max_y_offset = max(0.1, t_room["l"] - target_item["l"] - 0.1)
                
                pos_col1, pos_col2 = st.columns(2)
                with pos_col1:
                    new_rel_x = st.slider(
                        f"방 안의 X 위치 (m) [최대 {max_x_offset:.1f}m]:",
                        min_value=0.0, max_value=float(max_x_offset),
                        value=min(float(target_item.get("rel_x", 0.5)), float(max_x_offset)),
                        step=0.1, key=f"pos_x_{sel_item_name}"
                    )
                with pos_col2:
                    new_rel_y = st.slider(
                        f"방 안의 Y 위치 (m) [최대 {max_y_offset:.1f}m]:",
                        min_value=0.0, max_value=float(max_y_offset),
                        value=min(float(target_item.get("rel_y", 0.5)), float(max_y_offset)),
                        step=0.1, key=f"pos_y_{sel_item_name}"
                    )
                
                target_item["rel_x"] = new_rel_x
                target_item["rel_y"] = new_rel_y

    # 새 가구 추가 기능
    existing_furniture_names = ["바닥 (z=0)"] + [item["name"] for item in st.session_state.custom_items if item["type"] == "일반 가구"]
    with st.expander("➕ 새 가구 추가하기", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name = st.text_input("가구 이름:", value="공기청정기")
            new_room = st.selectbox("배치할 방 선택:", options=list(all_rooms.keys()))
        with c2:
            new_type = st.selectbox("유형:", options=["일반 가구", "러그/카페트 (바닥)", "벽걸이 액자 (벽면)"])
            new_base = st.selectbox("배치 기준 (가구 상단 올려놓기):", options=existing_furniture_names)
            new_color = st.color_picker("색상:", value="#E0E0E0")
        with c3:
            nw = st.number_input("가로 (m):", min_value=0.05, max_value=20.0, value=0.5, step=0.05)
            nl = st.number_input("세로 (m):", min_value=0.05, max_value=20.0, value=0.5, step=0.05)
            nh = st.number_input("높이 (m):", min_value=0.01, max_value=5.0, value=0.8, step=0.05)

        if st.button("➕ 가구 추가"):
            st.session_state.custom_items.append({
                "name": new_name, "room": new_room, "type": new_type, "base_item": new_base,
                "rel_x": 0.5, "rel_y": 0.5, "w": nw, "l": nl, "h": nh, "color": new_color
            })
            st.success(f"'{new_name}' 가구가 추가되었습니다!")
            st.rerun()

    valid_items = [item for item in st.session_state.custom_items if item["room"] in all_rooms]

    st.divider()

    # -------------------------------------------------------------
    # [시각화 옵션] 라벨 클러터(혼잡) 방지 옵션
    # -------------------------------------------------------------
    st.subheader("🏗️ 4. 정밀 3D 건축 평면도 시각화")
    
    vis_col1, vis_col2 = st.columns([2, 2])
    with vis_col1:
        show_furniture_labels = st.checkbox("🏷️ 가구 이름 3D 글자 항상 표시 (체크 해제 시 마우스 오버로 깔끔하게 확인)", value=False)
    with vis_col2:
        show_room_labels = st.checkbox("📌 방 이름 3D 글자 표시", value=True)

    fig = go.Figure()

    # 1) 바닥 타일 생성
    for rname, rdata in all_rooms.items():
        rx0, ry0, rw, rl, rz = rdata["x0"], rdata["y0"], rdata["w"], rdata["l"], rdata["z"]
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx0+rw, rx0+rw, rx0],
            y=[ry0, ry0, ry0+rl, ry0+rl],
            z=[rz, rz, rz, rz],
            color=rdata["color"], opacity=0.75, name=rname,
            hoverinfo="name"
        ))
        if show_room_labels:
            fig.add_trace(go.Scatter3d(
                x=[rx0 + rw/2], y=[ry0 + rl/2], z=[rz + 0.15],
                text=[f"<b>{rname}</b>"], mode="text", showlegend=False, hoverinfo="text"
            ))

    # 2) 1층 외벽, 내벽, 문, 창문 구축
    ent_info = rooms_1f["[1층] 현관 (Entrance)"]
    
    # 메인 현관문
    fig.add_trace(create_3d_box(ent_info["x0"], house_l - wall_th, 0, ent_info["w"]*0.15, wall_th, house_h*0.85, "#424242", "외벽"))
    if show_front_door:
        fig.add_trace(create_3d_box(ent_info["x0"] + ent_info["w"]*0.15, house_l - wall_th, 0, 1.1, wall_th, house_h*0.85, "#212121", "🚪 메인 현관문", opacity=0.98))
    fig.add_trace(create_3d_box(ent_info["x0"] + ent_info["w"]*0.15 + 1.1, house_l - wall_th, 0, ent_info["w"] - (ent_info["w"]*0.15 + 1.1), wall_th, house_h*0.85, "#424242", "외벽"))

    # 외벽 전체
    fig.add_trace(create_3d_box(0, 0, 0, rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.3, wall_th, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.3, 0, win_h_start, rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.4, wall_th, win_h, "#81D4FA", "1층 거실 창문", opacity=0.5))
    fig.add_trace(create_3d_box(rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.7, 0, 0, house_w - rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.7, wall_th, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(0, 0, 0, wall_th, house_l, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(house_w - wall_th, 0, 0, wall_th, house_l, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(0, house_l - wall_th, 0, ent_info["x0"], wall_th, house_h*0.85, "#616161", "후면 외벽"))

    # 내벽 구축
    fig.add_trace(create_3d_box(x_mid1 - wall_th/2, 0, 0, wall_th, y_mid * 0.3, house_h*0.85, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(x_mid1 - wall_th/2, y_mid * 0.3, 0, wall_th, door_w, house_h*0.75, "#8D6E63", "안방문", opacity=0.95))
    fig.add_trace(create_3d_box(x_mid1 - wall_th/2, y_mid * 0.3 + door_w, 0, wall_th, y_mid - (y_mid * 0.3 + door_w), house_h*0.85, "#9E9E9E", "내벽"))

    fig.add_trace(create_3d_box(0, y_mid - wall_th/2, 0, x_mid2 * 0.2, wall_th, house_h*0.85, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(x_mid2 * 0.2, y_mid - wall_th/2, 0, door_w, wall_th, house_h*0.75, "#8D6E63", "작은방문", opacity=0.95))
    fig.add_trace(create_3d_box(x_mid2 * 0.2 + door_w, y_mid - wall_th/2, 0, x_mid2 - (x_mid2 * 0.2 + door_w), wall_th, house_h*0.85, "#9E9E9E", "내벽"))

    pass_w = 1.2
    p_wall_w = (x_mid3 - x_mid2 - pass_w) / 2
    if p_wall_w > 0:
        fig.add_trace(create_3d_box(x_mid2, y_mid - wall_th/2, 0, p_wall_w, wall_th, house_h*0.85, "#9E9E9E", "내벽"))
        fig.add_trace(create_3d_box(x_mid2 + p_wall_w + pass_w, y_mid - wall_th/2, 0, p_wall_w, wall_th, house_h*0.85, "#9E9E9E", "내벽"))

    fig.add_trace(create_3d_box(x_mid3, y_mid - wall_th/2, 0, house_w - x_mid3, wall_th, house_h*0.85, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(x_mid2 - wall_th/2, y_mid, 0, wall_th, house_l - y_mid, house_h*0.85, "#9E9E9E", "내벽"))

    b_wall_l = y_bath - y_mid
    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_mid, 0, wall_th, b_wall_l * 0.2, house_h*0.85, "#9E9E9E", "욕실 벽체"))
    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_mid + b_wall_l * 0.2, 0, wall_th, door_w, house_h*0.75, "#00ACC1", "🚿 욕실문", opacity=0.95))
    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_mid + b_wall_l * 0.2 + door_w, 0, wall_th, b_wall_l - (b_wall_l * 0.2 + door_w), house_h*0.85, "#9E9E9E", "욕실 벽체"))

    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_bath, 0, wall_th, house_l - y_bath, house_h*0.85, "#9E9E9E", "현관 내벽"))
    fig.add_trace(create_3d_box(x_mid3, y_bath - wall_th/2, 0, house_w - x_mid3, wall_th, house_h*0.85, "#9E9E9E", "내벽"))

    # 커스텀 구조물 렌더링
    if "custom_structures" in st.session_state and st.session_state.custom_structures:
        for cs in st.session_state.custom_structures:
            rinfo = all_rooms[cs["room"]]
            rx0, ry0, rw, rl, rz = rinfo["x0"], rinfo["y0"], rinfo["w"], rinfo["l"], rinfo["z"]
            offset = cs["offset"]
            
            if cs["wall"] == "전면(남측)":
                cx0, cy0 = rx0 + offset, ry0
                c_dx, c_dy = cs["w"], wall_th
            elif cs["wall"] == "후면(북측)":
                cx0, cy0 = rx0 + offset, ry0 + rl - wall_th
                c_dx, c_dy = cs["w"], wall_th
            elif cs["wall"] == "좌측(서측)":
                cx0, cy0 = rx0, ry0 + offset
                c_dx, c_dy = wall_th, cs["w"]
            else:
                cx0, cy0 = rx0 + rw - wall_th, ry0 + offset
                c_dx, c_dy = wall_th, cs["w"]

            cz0 = rz + cs["z"]
            c_color = "#00E676" if "창문" in cs["type"] else ("#FF9100" if "문" in cs["type"] else "#757575")
            c_opacity = 0.6 if "창문" in cs["type"] else 0.95
            
            fig.add_trace(create_3d_box(cx0, cy0, cz0, c_dx, c_dy, cs["h"], c_color, f"🛠️ 개조 {cs['type']}", opacity=c_opacity))

    # 3) 가구 배치 및 수직 적치 (Stacking) 계산
    placed_coords = {}
    floor_items = [item for item in valid_items if item["base_item"] == "바닥 (z=0)"]
    stacked_items = [item for item in valid_items if item["base_item"] != "바닥 (z=0)"]

    # 바닥 가구 배치
    for item in floor_items:
        rname = item["room"]
        itype = item["type"]
        w, l, h = item["w"], item["l"], item["h"]
        rinfo = all_rooms[rname]
        rx0, ry0, rw, rl, rz = rinfo["x0"], rinfo["y0"], rinfo["w"], rinfo["l"], rinfo["z"]

        rel_x = float(item.get("rel_x", 0.3))
        rel_y = float(item.get("rel_y", 0.3))

        x0 = rx0 + rel_x
        y0 = ry0 + rel_y

        if itype == "러그/카페트 (바닥)":
            z0 = rz + 0.01
            h_actual = 0.02
        elif itype == "벽걸이 액자 (벽면)":
            z0 = rz + 1.3
            h_actual = h
        else:
            z0 = rz
            h_actual = h

        # 안전 범위 조절
        x0 = max(rx0 + 0.05, min(x0, rx0 + rw - w - 0.05))
        y0 = max(ry0 + 0.05, min(y0, ry0 + rl - l - 0.05))

        placed_coords[item["name"]] = (x0, y0, z0, w, l, h_actual)

        fig.add_trace(create_3d_box(x0, y0, z0, w, l, h_actual, item["color"], f"[{rname.split(' ')[0]}] {item['name']}"))
        
        if show_furniture_labels:
            fig.add_trace(go.Scatter3d(
                x=[x0 + w/2], y=[y0 + l/2], z=[z0 + h_actual + 0.15],
                text=[f"<b>{item['name']}</b>"], mode="text", showlegend=False, hoverinfo="text"
            ))

    # 수직 상단 적치 가구 (TV, 쿠션, 모니터, 스탠드 조명 등)
    for item in stacked_items:
        parent_name = item["base_item"]
        if parent_name in placed_coords:
            px0, py0, pz0, pw, pl, ph = placed_coords[parent_name]
            w, l, h = item["w"], item["l"], item["h"]

            rel_x = float(item.get("rel_x", 0.1))
            rel_y = float(item.get("rel_y", 0.1))

            x0 = px0 + rel_x
            y0 = py0 + rel_y
            z0 = pz0 + ph  # 부모 가구 높이 위에 완벽 부착!

            placed_coords[item["name"]] = (x0, y0, z0, w, l, h)

            fig.add_trace(create_3d_box(x0, y0, z0, w, l, h, item["color"], f"[{parent_name} 위] {item['name']}"))
            
            if show_furniture_labels:
                fig.add_trace(go.Scatter3d(
                    x=[x0 + w/2], y=[y0 + l/2], z=[z0 + h + 0.15],
                    text=[f"<b>{item['name']}</b>"], mode="text", showlegend=False, hoverinfo="text"
                ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='가로 (m)', range=[-0.5, house_w + 0.5]),
            yaxis=dict(title='세로 (m)', range=[-0.5, house_l + 0.5]),
            zaxis=dict(title='높이 (m)', range=[0, total_render_height + 0.5]),
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.4))
        ),
        width=950, height=720,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ 오류 발생: {e}")
