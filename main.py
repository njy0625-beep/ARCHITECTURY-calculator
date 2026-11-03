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
    # [3D 자유 개조 옵션] 사용자가 직접 문/창문 추가하기
    # -------------------------------------------------------------
    st.divider()
    with st.expander("🛠️ 3D 건축 수동 개조 (사용자 지정 문 & 창문 자유 추가)", expanded=False):
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            m_type = st.selectbox("개조 구조물 종류:", options=["창문 (Window)", "방문/출입문 (Door)"])
            m_room = st.selectbox("설치할 공간 위치:", options=list(all_rooms.keys()))
        with col_m2:
            m_wall_pos = st.selectbox("벽면 방향:", options=["전면(남측)", "후면(북측)", "좌측(서측)", "우측(동측)"])
            m_w = st.number_input("가로 폭 (m):", min_value=0.5, max_value=5.0, value=1.2, step=0.1)
        with col_m3:
            m_h = st.number_input("높이 (m):", min_value=0.5, max_value=3.0, value=1.2, step=0.1)
            m_z = st.number_input("바닥에서의 높이 Z (m):", min_value=0.0, max_value=4.0, value=0.9, step=0.1)
        with col_m4:
            st.write(" ")
            st.write(" ")
            if st.button("🔨 건축 개조 추가하기"):
                if "custom_structures" not in st.session_state:
                    st.session_state.custom_structures = []
                st.session_state.custom_structures.append({
                    "type": m_type, "room": m_room, "wall": m_wall_pos,
                    "w": m_w, "h": m_h, "z": m_z
                })
                st.success("새 개조 건축 요소가 반영되었습니다!")
                st.rerun()

        if "custom_structures" in st.session_state and st.session_state.custom_structures:
            st.markdown("##### 🛠️ 현재 추가된 커스텀 개조 구조물")
            for cs_idx, cs in enumerate(st.session_state.custom_structures):
                cs_col1, cs_col2 = st.columns([4, 1])
                cs_col1.write(f"• **[{cs['room']}]** {cs['wall']} - {cs['type']} (폭: {cs['w']}m, 높이: {cs['h']}m, 높이Z: {cs['z']}m)")
                if cs_col2.button("삭제", key=f"del_cs_{cs_idx}"):
                    st.session_state.custom_structures.pop(cs_idx)
                    st.rerun()

    st.divider()

    # -------------------------------------------------------------
    # [입력 2] 풍부한 풀옵션 기본 디테일 가구 세팅
    # -------------------------------------------------------------
    st.subheader("2. 가구, 소품 및 수직 적치(Stacking) 등록")
    st.caption("💡 **벽걸이(액자/거울/선반)**, **바닥 러그/카페트**, **디테일 소품(쿠션/식기/조명)**이 대폭 보강되었습니다.")

    if "custom_items" not in st.session_state:
        st.session_state.custom_items = [
            # [현관]
            {"name": "🚪 현관 슬라이딩 중문", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.0, "l": 0.1, "h": 2.1, "color": "#3E2723"},
            {"name": "신발장 및 전신거울", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.1, "l": 0.4, "h": 1.4, "color": "#795548"},
            {"name": "현관 바닥 매트", "room": "[1층] 현관 (Entrance)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "w": 0.8, "l": 0.5, "h": 0.02, "color": "#9E9E9E"},
            
            # [거실]
            {"name": "4인용 패브릭 소파", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 2.4, "l": 0.9, "h": 0.85, "color": "#5C6BC0"},
            {"name": "소파 인테리어 쿠션", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "4인용 패브릭 소파", "w": 0.5, "l": 0.4, "h": 0.25, "color": "#FF8A65"},
            {"name": "원목 소파 테이블", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.1, "l": 0.6, "h": 0.4, "color": "#8D6E63"},
            {"name": "대형 거실 TV장", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 2.0, "l": 0.4, "h": 0.5, "color": "#4E342E"},
            {"name": "75인치 스마트 TV", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "대형 거실 TV장", "w": 1.6, "l": 0.15, "h": 0.9, "color": "#1A237E"},
            {"name": "샤기 거실 패턴 러그", "room": "[1층] 거실 (Living Room)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "w": 2.4, "l": 1.8, "h": 0.02, "color": "#FFE082"},
            {"name": "🖼️ 대형 갤러리 벽걸이 액자", "room": "[1층] 거실 (Living Room)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "w": 1.5, "l": 0.08, "h": 0.9, "color": "#FFB300"},
            
            # [안방]
            {"name": "퀸 사이즈 침대", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.6, "l": 2.1, "h": 0.55, "color": "#3949AB"},
            {"name": "안방 대형 붙박이장", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 2.0, "l": 0.65, "h": 2.1, "color": "#6D4C41"},
            {"name": "원목 침대 협탁", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 0.5, "l": 0.4, "h": 0.5, "color": "#A1887F"},
            {"name": "무드 스탠드 조명", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "원목 침대 협탁", "w": 0.25, "l": 0.25, "h": 0.4, "color": "#FFF176"},
            {"name": "침실 원형 카페트", "room": "[1층] 안방 (Master Bedroom)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "w": 1.8, "l": 1.8, "h": 0.02, "color": "#CE93D8"},
            {"name": "🖼️ 안방 인테리어 유화 액자", "room": "[1층] 안방 (Master Bedroom)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "w": 1.0, "l": 0.08, "h": 0.7, "color": "#BA68C8"},

            # [작은방]
            {"name": "슈퍼싱글 침대", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.1, "l": 2.0, "h": 0.5, "color": "#0288D1"},
            {"name": "1인용 집중 스터디 책상", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.2, "l": 0.7, "h": 0.75, "color": "#26A69A"},
            {"name": "데스크탑 32인치 모니터", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "1인용 집중 스터디 책상", "w": 0.6, "l": 0.2, "h": 0.45, "color": "#212121"},
            {"name": "🖼️ 벽걸이 책선반", "room": "[1층] 작은방 (Bedroom 2)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "w": 1.2, "l": 0.15, "h": 0.3, "color": "#8D6E63"},

            # [주방/식당]
            {"name": "4인용 아일랜드 식탁", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.4, "l": 0.8, "h": 0.75, "color": "#66BB6A"},
            {"name": "양문형 대형 비스포크 냉장고", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 0.95, "l": 0.9, "h": 1.85, "color": "#78909C"},
            {"name": "🖼️ 주방 벽걸이 와인 수납장", "room": "[1층] 주방/식당 (Kitchen)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "w": 1.0, "l": 0.2, "h": 0.5, "color": "#5D4037"},

            # [욕실/화장실]
            {"name": "양변기 & 세면대 세트", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.0, "l": 0.6, "h": 0.8, "color": "#00BCD4"},
            {"name": "유리 샤워부스/욕조", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.0, "l": 0.9, "h": 1.9, "color": "#4DD0E1"},
            {"name": "🖼️ 욕실 슬라이딩 거울 수납장", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "w": 0.8, "l": 0.15, "h": 0.6, "color": "#B2EBF2"}
        ]

    # 세션 방 이름 자동 보정
    for item in st.session_state.custom_items:
        if not (item["room"].startswith("[1층]") or item["room"].startswith("[2층]")):
            item["room"] = f"[1층] {item['room']}"

    existing_furniture_names = ["바닥 (z=0)"] + [item["name"] for item in st.session_state.custom_items if item["type"] == "일반 가구"]

    with st.expander("➕ 새 커스텀 가구/소품 추가하기", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name = st.text_input("아이템 이름:", value="공기청정기")
            new_room = st.selectbox("배치할 방 선택:", options=list(all_rooms.keys()))
        with c2:
            new_type = st.selectbox("아이템 유형:", options=["일반 가구", "러그/카페트 (바닥)", "벽걸이 액자 (벽면)"])
            new_base = st.selectbox("배치 위치 (가구 위 올려놓기):", options=existing_furniture_names)
            new_color = st.color_picker("3D 색상 선택:", value="#E0E0E0")
        with c3:
            st.markdown("**3D 규격 입력 (m)**")
            nw = st.number_input("가로 (m):", min_value=0.05, max_value=20.0, value=0.4, step=0.05)
            nl = st.number_input("세로 (m):", min_value=0.05, max_value=20.0, value=0.4, step=0.05)
            nh = st.number_input("높이 (m):", min_value=0.01, max_value=5.0, value=0.8, step=0.05)

        if st.button("➕ 이 항목 추가하기"):
            st.session_state.custom_items.append({
                "name": new_name, "room": new_room, "type": new_type, "base_item": new_base,
                "w": nw, "l": nl, "h": nh, "color": new_color
            })
            st.success(f"'{new_name}' 항목이 추가되었습니다!")
            st.rerun()

    valid_items = [item for item in st.session_state.custom_items if item["room"] in all_rooms]
    st.markdown("##### 📋 현재 주택 내 등록된 디테일 가구/소품 목록 (총 {}개)".format(len(valid_items)))
    if valid_items:
        items_to_remove = []
        for idx, item in enumerate(st.session_state.custom_items):
            if item["room"] not in all_rooms:
                continue
            ic1, ic2, ic3, ic4 = st.columns([3, 2, 3, 1])
            base_str = f" ➔ [{item['base_item']}] 위" if item['base_item'] != "바닥 (z=0)" else ""
            ic1.write(f"**{item['room'].split(' ')[0]}** {item['name']}{base_str}")
            ic2.write(f"유형: {item['type']}")
            ic3.write(f"치수: {item['w']}m × {item['l']}m × H:{item['h']}m")
            if ic4.button("삭제", key=f"del_{idx}"):
                items_to_remove.append(idx)

        for idx in sorted(items_to_remove, reverse=True):
            st.session_state.custom_items.pop(idx)
            st.rerun()

    st.divider()

    # [출력 1] 종합 진단
    st.subheader("📊 3. 건축 연면적 및 주거 쾌적도 종합 진단")
    total_furniture_area = sum(item["w"] * item["l"] for item in valid_items if item["type"] == "일반 가구" and item["base_item"] == "바닥 (z=0)")
    occupancy_ratio = (total_furniture_area / total_house_area) * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("총 연면적 (1층+2층)", f"{total_house_area:.2f} m²")
    m2.metric("바닥 가구 점유 면적", f"{total_furniture_area:.2f} m²")
    m3.metric("바닥 공간 점유율", f"{occupancy_ratio:.1f} %")
    m4.metric("여유 동선 확보율", f"{100-occupancy_ratio:.1f} %")

    st.divider()

    # [출력 2] 3D 정밀 건축 평면도 시각화
    st.subheader("🏗️ 4. 정밀 3D 건축 평면도 (현관문, 개조 구조물, 디테일 가구 통합 시각화)")
    st.caption("💡 **3D 도면 기호**: 🚪 **철제 메인 출입문** | 🧱 **회색 내/외벽** | 🖼️ **벽걸이 액자/거울** | 🟧 **바닥 패턴 러그** | 🪑 **디테일 가구**")

    fig = go.Figure()

    # 1) 바닥 타일 생성 (1층 및 2층)
    for rname, rdata in all_rooms.items():
        rx0, ry0, rw, rl, rz = rdata["x0"], rdata["y0"], rdata["w"], rdata["l"], rdata["z"]
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx0+rw, rx0+rw, rx0],
            y=[ry0, ry0, ry0+rl, ry0+rl],
            z=[rz, rz, rz, rz],
            color=rdata["color"], opacity=0.75, name=rname
        ))
        fig.add_trace(go.Scatter3d(
            x=[rx0 + rw/2], y=[ry0 + rl/2], z=[rz + 0.1],
            text=[f"<b>{rname}</b>"], mode="text", showlegend=False, hoverinfo="text"
        ))

    # -------------------------------------------------------------
    # 2) 1층 외벽, 내벽, 메인 현관문, 방문, 창문 완전 구축
    # -------------------------------------------------------------
    ent_info = rooms_1f["[1층] 현관 (Entrance)"]
    
    # 2-A: 외벽 & 🚪 메인 현관 출입문 (Front Entrance Door)
    fig.add_trace(create_3d_box(ent_info["x0"], house_l - wall_th, 0, ent_info["w"]*0.15, wall_th, house_h*0.85, "#424242", "외벽"))
    
    if show_front_door:
        # 🚪 메인 현관문 닫힘 상태 표기
        fig.add_trace(create_3d_box(ent_info["x0"] + ent_info["w"]*0.15, house_l - wall_th, 0, 1.1, wall_th, house_h*0.85, "#212121", "🚪 메인 현관문 (Front Door)", opacity=0.98))
        fig.add_trace(go.Scatter3d(
            x=[ent_info["x0"] + ent_info["w"]*0.15 + 0.55], y=[house_l - wall_th/2], z=[house_h*0.95],
            text=["<b>🚪 메인 현관문 (닫힘)</b>"], mode="text", showlegend=False, hoverinfo="text"
        ))
    
    fig.add_trace(create_3d_box(ent_info["x0"] + ent_info["w"]*0.15 + 1.1, house_l - wall_th, 0, ent_info["w"] - (ent_info["w"]*0.15 + 1.1), wall_th, house_h*0.85, "#424242", "외벽"))

    # 외벽 전체 (조절된 house_h 높이 적용)
    fig.add_trace(create_3d_box(0, 0, 0, rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.3, wall_th, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.3, 0, win_h_start, rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.4, wall_th, win_h, "#81D4FA", "1층 거실 창문", opacity=0.5))
    fig.add_trace(create_3d_box(rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.7, 0, 0, house_w - rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.7, wall_th, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(0, 0, 0, wall_th, house_l, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(house_w - wall_th, 0, 0, wall_th, house_l, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(0, house_l - wall_th, 0, ent_info["x0"], wall_th, house_h*0.85, "#616161", "후면 외벽"))

    # 2-B: 1층 내부 모든 내벽 구축
    # 1) 거실 - 안방 내벽 & 안방문
    fig.add_trace(create_3d_box(x_mid1 - wall_th/2, 0, 0, wall_th, y_mid * 0.3, house_h*0.85, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(x_mid1 - wall_th/2, y_mid * 0.3, 0, wall_th, door_w, house_h*0.75, "#8D6E63", "안방문 (Door)", opacity=0.95))
    fig.add_trace(create_3d_box(x_mid1 - wall_th/2, y_mid * 0.3 + door_w, 0, wall_th, y_mid - (y_mid * 0.3 + door_w), house_h*0.85, "#9E9E9E", "내벽"))

    # 2) 가로 중앙 내벽 (거실 ↔ 작은방)
    fig.add_trace(create_3d_box(0, y_mid - wall_th/2, 0, x_mid2 * 0.2, wall_th, house_h*0.85, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(x_mid2 * 0.2, y_mid - wall_th/2, 0, door_w, wall_th, house_h*0.75, "#8D6E63", "작은방문 (Door)", opacity=0.95))
    fig.add_trace(create_3d_box(x_mid2 * 0.2 + door_w, y_mid - wall_th/2, 0, x_mid2 - (x_mid2 * 0.2 + door_w), wall_th, house_h*0.85, "#9E9E9E", "내벽"))

    # 3) 주방 통로 파티션
    pass_w = 1.2
    p_wall_w = (x_mid3 - x_mid2 - pass_w) / 2
    if p_wall_w > 0:
        fig.add_trace(create_3d_box(x_mid2, y_mid - wall_th/2, 0, p_wall_w, wall_th, house_h*0.85, "#9E9E9E", "내벽"))
        fig.add_trace(create_3d_box(x_mid2 + p_wall_w + pass_w, y_mid - wall_th/2, 0, p_wall_w, wall_th, house_h*0.85, "#9E9E9E", "내벽"))

    # 4) 안방 ↔ 욕실/현관 내벽
    fig.add_trace(create_3d_box(x_mid3, y_mid - wall_th/2, 0, house_w - x_mid3, wall_th, house_h*0.85, "#9E9E9E", "내벽"))

    # 5) 작은방 ↔ 주방 세로 내벽
    fig.add_trace(create_3d_box(x_mid2 - wall_th/2, y_mid, 0, wall_th, house_l - y_mid, house_h*0.85, "#9E9E9E", "내벽"))

    # 6) 주방 ↔ 욕실 세로 내벽 & 🚿 욕실문
    b_wall_l = y_bath - y_mid
    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_mid, 0, wall_th, b_wall_l * 0.2, house_h*0.85, "#9E9E9E", "욕실 벽체"))
    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_mid + b_wall_l * 0.2, 0, wall_th, door_w, house_h*0.75, "#00ACC1", "🚿 욕실문", opacity=0.95))
    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_mid + b_wall_l * 0.2 + door_w, 0, wall_th, b_wall_l - (b_wall_l * 0.2 + door_w), house_h*0.85, "#9E9E9E", "욕실 벽체"))

    # 7) 주방 ↔ 현관 세로 내벽 & 욕실 ↔ 현관 가로 내벽
    fig.add_trace(create_3d_box(x_mid3 - wall_th/2, y_bath, 0, wall_th, house_l - y_bath, house_h*0.85, "#9E9E9E", "현관 내벽"))
    fig.add_trace(create_3d_box(x_mid3, y_bath - wall_th/2, 0, house_w - x_mid3, wall_th, house_h*0.85, "#9E9E9E", "내벽"))

    # -------------------------------------------------------------
    # 2-C: 사용자 지정 커스텀 개조 구조물 (문/창문) 렌더링
    # -------------------------------------------------------------
    if "custom_structures" in st.session_state and st.session_state.custom_structures:
        for cs in st.session_state.custom_structures:
            rinfo = all_rooms[cs["room"]]
            rx0, ry0, rw, rl, rz = rinfo["x0"], rinfo["y0"], rinfo["w"], rinfo["l"], rinfo["z"]
            
            # 벽 위치 계산
            if cs["wall"] == "전면(남측)":
                cx0, cy0 = rx0 + rw/2 - cs["w"]/2, ry0
                c_dx, c_dy = cs["w"], wall_th
            elif cs["wall"] == "후면(북측)":
                cx0, cy0 = rx0 + rw/2 - cs["w"]/2, ry0 + rl - wall_th
                c_dx, c_dy = cs["w"], wall_th
            elif cs["wall"] == "좌측(서측)":
                cx0, cy0 = rx0, ry0 + rl/2 - cs["w"]/2
                c_dx, c_dy = wall_th, cs["w"]
            else: # 우측(동측)
                cx0, cy0 = rx0 + rw - wall_th, ry0 + rl/2 - cs["w"]/2
                c_dx, c_dy = wall_th, cs["w"]

            cz0 = rz + cs["z"]
            c_color = "#00E676" if "창문" in cs["type"] else "#FF9100"
            c_opacity = 0.6 if "창문" in cs["type"] else 0.95
            
            fig.add_trace(create_3d_box(cx0, cy0, cz0, c_dx, c_dy, cs["h"], c_color, f"🛠️ 커스텀 {cs['type']}", opacity=c_opacity))
            fig.add_trace(go.Scatter3d(
                x=[cx0 + c_dx/2], y=[cy0 + c_dy/2], z=[cz0 + cs["h"] + 0.2],
                text=[f"<b>🛠️ 개조 {cs['type']}</b>"], mode="text", showlegend=False, hoverinfo="text"
            ))

    # -------------------------------------------------------------
    # 3) 2층 옵션 활성화 시: 2층 구조물 구축
    # -------------------------------------------------------------
    if use_2nd_floor:
        stair_x = house_w * 0.35
        stair_y = house_l * 0.45
        stair_w = 1.2
        stair_l = 1.8
        stair_traces = create_stairs(stair_x, stair_y, 0, stair_w, stair_l, house_h, num_steps=10, color="#8D6E63", name="🪜 연결 계단")
        for trace in stair_traces:
            fig.add_trace(trace)

        z2 = house_h
        fig.add_trace(create_3d_box(0, 0, z2, house_w*0.3, wall_th, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(house_w*0.3, 0, z2 + win_h_start, house_w*0.4, wall_th, win_h, "#81D4FA", "2층 전면 창문", opacity=0.5))
        fig.add_trace(create_3d_box(house_w*0.7, 0, z2, house_w*0.3, wall_th, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(0, 0, z2, wall_th, house_l, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(house_w - wall_th, 0, z2, wall_th, house_l, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(0, house_l - wall_th, z2, house_w, wall_th, house_h*0.85, "#546E7A", "2층 후면 외벽"))
        fig.add_trace(create_3d_box(house_w*0.5 - wall_th/2, 0, z2, wall_th, house_l*0.55, house_h*0.85, "#B0BEC5", "2층 내벽"))

    # -------------------------------------------------------------
    # 4) 가구 및 수직 적치(Stacking) 배치
    # -------------------------------------------------------------
    placed_coords = {}
    room_offsets = {rname: {"cx": rdata["x0"] + 0.35, "cy": rdata["y0"] + 0.35} for rname, rdata in all_rooms.items()}

    floor_items = [item for item in valid_items if item["base_item"] == "바닥 (z=0)"]
    stacked_items = [item for item in valid_items if item["base_item"] != "바닥 (z=0)"]

    # 1단계: 바닥 가구 배치
    for item in floor_items:
        rname = item["room"]
        itype = item["type"]
        w, l, h = item["w"], item["l"], item["h"]
        rinfo = all_rooms[rname]
        rx0, ry0, rw, rl, rz = rinfo["x0"], rinfo["y0"], rinfo["w"], rinfo["l"], rinfo["z"]

        if itype == "러그/카페트 (바닥)":
            x0 = rx0 + (rw - w) / 2
            y0 = ry0 + (rl - l) / 2
            z0 = rz + 0.01
            h_actual = 0.02
        elif itype == "벽걸이 액자 (벽면)":
            x0 = rx0 + 0.2
            y0 = ry0 + rl - l - 0.2
            z0 = rz + 1.3
            h_actual = h
        else:
            cx = room_offsets[rname]["cx"]
            cy = room_offsets[rname]["cy"]
            if cx + w <= rx0 + rw - 0.25 and cy + l <= ry0 + rl - 0.25:
                x0, y0 = cx, cy
                room_offsets[rname]["cx"] += (w + 0.25)
            else:
                room_offsets[rname]["cx"] = rx0 + 0.35
                room_offsets[rname]["cy"] += (l + 0.25)
                x0 = room_offsets[rname]["cx"]
                y0 = room_offsets[rname]["cy"]
            z0 = rz
            h_actual = h

        x0 = max(rx0 + 0.1, min(x0, rx0 + rw - w - 0.1))
        y0 = max(ry0 + 0.1, min(y0, ry0 + rl - l - 0.1))

        placed_coords[item["name"]] = (x0, y0, z0, w, l, h_actual)

        fig.add_trace(create_3d_box(x0, y0, z0, w, l, h_actual, item["color"], f"[{rname.split(' ')[0]}] {item['name']}"))
        fig.add_trace(go.Scatter3d(
            x=[x0 + w/2], y=[y0 + l/2], z=[z0 + h_actual + 0.15],
            text=[f"<b>{item['name']}</b>"], mode="text", showlegend=False, hoverinfo="text"
        ))

    # 2단계: 가구 상단 수직 적치(Stacking)
    for item in stacked_items:
        parent_name = item["base_item"]
        if parent_name in placed_coords:
            px0, py0, pz0, pw, pl, ph = placed_coords[parent_name]
            w, l, h = item["w"], item["l"], item["h"]

            x0 = px0 + (pw - w) / 2
            y0 = py0 + (pl - l) / 2
            z0 = pz0 + ph

            placed_coords[item["name"]] = (x0, y0, z0, w, l, h)

            fig.add_trace(create_3d_box(x0, y0, z0, w, l, h, item["color"], f"[{parent_name} 위] {item['name']}"))
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
        width=950,
        height=720,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # [출력 3] 개조 가이드
    st.subheader("💡 5. 수동 건축 개조 및 가구 디테일 설정 가이드")
    st.write("• **🚪 메인 현관문 닫힘 옵션**: 상단 '🚪 현관 중문/출입문 닫힘 표시'를 체크하면 입구에 진한 3D 현관문이 정밀 배치됩니다.")
    st.write("• **📐 3D 벽 높이 수동 조절**: 슬라이더를 이용해 1.0m ~ 6.0m까지 벽의 높이를 자유롭게 위로 늘리거나 낮출 수 있습니다.")
    st.write("• **🛠️ 사용자 지정 문/창문 추가**: '3D 건축 수동 개조' 메뉴에서 원하는 방과 벽면 방향을 선택하여 커스텀 창문과 문을 3D 도면에 직접 뚫어 넣을 수 있습니다.")

except ValueError:
    st.error("❌ 올바른 숫자를 입력해 주세요.")
except Exception as e:
    st.error(f"❌ 오류 발생: {e}")
