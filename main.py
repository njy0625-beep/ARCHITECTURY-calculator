import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 복층(2층) 건축 평면도 & 가구 배치 시스템", page_icon="🏛️", layout="wide")

st.title("🏛️ AI 기반 3D 정밀 주택 평면도 & 복층(2층) 확장 가구 배치 시스템")
st.caption("최대 100m까지 대형 주택 확장이 가능하며, **2층(복층) 구조 온/오프 토글 스위치** 및 **연결 계단(Stairs)**을 완벽 시각화합니다.")

st.divider()

# -------------------------------------------------------------
# 2. 3D 메쉬 생성 헬퍼 함수
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
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        name=name,
        showscale=False,
        flatshading=True,
        hoverinfo="name"
    )

def create_stairs(x0, y0, z0, dx, dy, dz, num_steps=10, color="#8D6E63", name="연결 계단"):
    """3D 입체 계단 생성 함수"""
    traces = []
    step_h = dz / num_steps
    step_l = dy / num_steps
    for step in range(num_steps):
        sz0 = z0 + step * step_h
        sy0 = y0 + step * step_l
        traces.append(create_3d_box(x0, sy0, sz0, dx, step_l, step_h, color, f"{name} ({step+1}단)"))
    return traces

# -------------------------------------------------------------
# 3. 메인 프로그램 (예외 처리 구조)
# -------------------------------------------------------------
try:
    # [입력 1] 전체 집 구조 설정 (최대 100m 확장 지원)
    st.subheader("1. 집 전체 치수 및 복층(2층) 옵션 설정")
    
    col_hw, col_hl, col_hh, col_toggle = st.columns([2, 2, 2, 3])
    with col_hw:
        house_w = st.number_input("집 전체 가로 (m):", min_value=5.0, max_value=100.0, value=10.0, step=0.5)
    with col_hl:
        house_l = st.number_input("집 전체 세로 (m):", min_value=5.0, max_value=100.0, value=8.0, step=0.5)
    with col_hh:
        house_h = st.number_input("층당 천장 높이 (m):", min_value=2.0, max_value=5.0, value=2.5, step=0.1)
    with col_toggle:
        st.write("**복층(2층) 구조 옵션**")
        use_2nd_floor = st.checkbox("🏢 2층(복층) 구조 활성화", value=False)

    if house_w <= 0 or house_l <= 0 or house_h <= 0:
        st.warning("⚠️ 모든 치수는 0보다 커야 합니다.")
        st.stop()

    num_floors = 2 if use_2nd_floor else 1
    total_house_area = house_w * house_l * num_floors
    pyeong = total_house_area / 3.3058
    total_render_height = house_h * num_floors

    st.info(f"🏡 전체 주택 연면적: **{total_house_area:.2f} m²** (약 {pyeong:.1f}평) | 층수: **{num_floors}층** | 총 높이: **{total_render_height:.1f} m**")

    # -------------------------------------------------------------
    # AI 자동 방 구획 분할 (1층 & 2층)
    # -------------------------------------------------------------
    wall_th = 0.15  # 표준 벽체 두께 (15cm)
    door_w = 0.9    # 표준 문 폭
    win_h_start = 0.9
    win_h = 1.2

    # 1층 공간 구조
    rooms_1f = {
        "[1층] 거실 (Living Room)": {"x0": 0, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#FAFAFA", "z": 0},
        "[1층] 안방 (Master Bedroom)": {"x0": house_w * 0.5, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#F3E5F5", "z": 0},
        "[1층] 작은방 (Bedroom 2)": {"x0": 0, "y0": house_l * 0.55, "w": house_w * 0.38, "l": house_l * 0.45, "color": "#E1F5FE", "z": 0},
        "[1층] 주방/식당 (Kitchen)": {"x0": house_w * 0.38, "y0": house_l * 0.55, "w": house_w * 0.37, "l": house_l * 0.45, "color": "#FFF3E0", "z": 0},
        "[1층] 욕실/화장실 (Bathroom)": {"x0": house_w * 0.75, "y0": house_l * 0.55, "w": house_w * 0.25, "l": house_l * 0.25, "color": "#E0F7FA", "z": 0},
        "[1층] 현관 (Entrance)": {"x0": house_w * 0.75, "y0": house_l * 0.80, "w": house_w * 0.25, "l": house_l * 0.20, "color": "#E8EAF6", "z": 0}
    }

    # 2층 공간 구조 (2층 옵션 활성화 시 추가)
    rooms_2f = {}
    if use_2nd_floor:
        rooms_2f = {
            "[2층] 메인 서재/작업실 (Study)": {"x0": 0, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#EFEBE9", "z": house_h},
            "[2층] 게스트 룸 (Guest Room)": {"x0": house_w * 0.5, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#F1F8E9", "z": house_h},
            "[2층] 취미실/드레스룸 (Hobby Room)": {"x0": 0, "y0": house_l * 0.55, "w": house_w * 0.45, "l": house_l * 0.45, "color": "#FFF8E1", "z": house_h},
            "[2층] 2층 테라스/욕실 (Terrace & Bath)": {"x0": house_w * 0.45, "y0": house_l * 0.55, "w": house_w * 0.55, "l": house_l * 0.45, "color": "#E0F2F1", "z": house_h}
        }

    all_rooms = {**rooms_1f, **rooms_2f}

    st.divider()

    # [입력 2] 커스텀 가구 & 복층 대응 초기 프리셋
    st.subheader("2. 가구, 소품 및 수직 적치(Stacking) 등록")
    st.caption("💡 2층 스위치를 켜면 **2층 전용 방(서재, 게스트룸, 취미실 등) 선택 및 가구 배치**가 활성화됩니다.")

    if "custom_items" not in st.session_state:
        st.session_state.custom_items = [
            # 1층 기본 가구
            {"name": "신발장/수납장", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.0, "l": 0.4, "h": 1.2, "color": "#795548"},
            {"name": "4인용 패브릭 소파", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 2.4, "l": 0.9, "h": 0.85, "color": "#5C6BC0"},
            {"name": "원목 소파 테이블", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.1, "l": 0.6, "h": 0.4, "color": "#8D6E63"},
            {"name": "대형 거실 TV장", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 2.0, "l": 0.4, "h": 0.5, "color": "#4E342E"},
            {"name": "75인치 스마트 TV", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "대형 거실 TV장", "w": 1.6, "l": 0.15, "h": 0.9, "color": "#1A237E"},
            {"name": "퀸 사이즈 침대", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.6, "l": 2.1, "h": 0.55, "color": "#3949AB"},
            {"name": "4인용 아일랜드 식탁", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.4, "l": 0.8, "h": 0.75, "color": "#66BB6A"},
            {"name": "양변기 & 세면대 세트", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.0, "l": 0.6, "h": 0.8, "color": "#00BCD4"},
            # 2층 기본 가구 (2층 활성화 시 시각화)
            {"name": "2층 서재 대형 원목 책상", "room": "[2층] 메인 서재/작업실 (Study)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.8, "l": 0.8, "h": 0.75, "color": "#5D4037"},
            {"name": "2층 게스트 침대", "room": "[2층] 게스트 룸 (Guest Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.2, "l": 2.0, "h": 0.5, "color": "#00796B"}
        ]

    existing_furniture_names = ["바닥 (z=0)"] + [item["name"] for item in st.session_state.custom_items if item["type"] == "일반 가구"]

    with st.expander("➕ 새 가구/소품 직접 작성 및 추가하기", expanded=False):
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
    st.markdown("##### 📋 현재 주택 내 등록된 활성 가구/소품 목록 (총 {}개)".format(len(valid_items)))
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
    st.subheader("🏗️ 4. 정밀 3D 건축 평면도 (복층, 연결 계단, 문/창문, 가구 통합)")
    st.caption("💡 **3D 도면 기호**: 🚪 **진한 갈색/철제(메인 현관문)** | 🧱 **회색 벽체** | 🪜 **갈색 계단(Stairs)** | 💧 **민트색(욕실)** | 🪟 **창문**")

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
    # 2) 1층 외벽, 내벽, 문, 창문 구축
    # -------------------------------------------------------------
    ent_info = rooms_1f["[1층] 현관 (Entrance)"]
    fig.add_trace(create_3d_box(ent_info["x0"], house_l - wall_th, 0, ent_info["w"]*0.2, wall_th, house_h*0.85, "#424242", "외벽"))
    fig.add_trace(create_3d_box(ent_info["x0"] + ent_info["w"]*0.2, house_l - wall_th, 0, 1.0, wall_th, house_h*0.85, "#3E2723", "🚪 메인 현관문 (Front Door)", opacity=0.98))
    fig.add_trace(go.Scatter3d(
        x=[ent_info["x0"] + ent_info["w"]*0.2 + 0.5], y=[house_l - wall_th/2], z=[house_h*0.95],
        text=["<b>🚪 메인 현관문 (입구)</b>"], mode="text", showlegend=False, hoverinfo="text"
    ))
    fig.add_trace(create_3d_box(ent_info["x0"] + ent_info["w"]*0.2 + 1.0, house_l - wall_th, 0, ent_info["w"] - (ent_info["w"]*0.2 + 1.0), wall_th, house_h*0.85, "#424242", "외벽"))

    # 1층 외벽
    fig.add_trace(create_3d_box(0, 0, 0, rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.3, wall_th, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.3, 0, win_h_start, rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.4, wall_th, win_h, "#81D4FA", "1층 거실 창문", opacity=0.5))
    fig.add_trace(create_3d_box(rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.7, 0, 0, house_w - rooms_1f["[1층] 거실 (Living Room)"]["w"]*0.7, wall_th, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(0, 0, 0, wall_th, house_l, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(house_w - wall_th, 0, 0, wall_th, house_l, house_h*0.85, "#616161", "외벽"))
    fig.add_trace(create_3d_box(0, house_l - wall_th, 0, ent_info["x0"], wall_th, house_h*0.85, "#616161", "후면 외벽"))

    # 1층 내벽
    mid_y = rooms_1f["[1층] 거실 (Living Room)"]["l"]
    mid_x1 = rooms_1f["[1층] 거실 (Living Room)"]["w"]
    fig.add_trace(create_3d_box(mid_x1 - wall_th/2, 0, 0, wall_th, mid_y * 0.3, house_h*0.85, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(mid_x1 - wall_th/2, mid_y * 0.3, 0, wall_th, door_w, house_h*0.75, "#8D6E63", "안방문 (Door)", opacity=0.95))
    fig.add_trace(create_3d_box(mid_x1 - wall_th/2, mid_y * 0.3 + door_w, 0, wall_th, mid_y - (mid_y * 0.3 + door_w), house_h*0.85, "#9E9E9E", "내벽"))

    # 욕실 벽체 및 방문
    bath_info = rooms_1f["[1층] 욕실/화장실 (Bathroom)"]
    fig.add_trace(create_3d_box(bath_info["x0"] - wall_th/2, bath_info["y0"], 0, wall_th, bath_info["l"]*0.2, house_h*0.85, "#9E9E9E", "욕실 벽체"))
    fig.add_trace(create_3d_box(bath_info["x0"] - wall_th/2, bath_info["y0"] + bath_info["l"]*0.2, 0, wall_th, door_w, house_h*0.75, "#00ACC1", "🚿 욕실문", opacity=0.95))
    fig.add_trace(create_3d_box(bath_info["x0"] - wall_th/2, bath_info["y0"] + bath_info["l"]*0.2 + door_w, 0, wall_th, bath_info["l"] - (bath_info["l"]*0.2 + door_w), house_h*0.85, "#9E9E9E", "욕실 벽체"))

    # -------------------------------------------------------------
    # 3) 2층 옵션 활성화 시: 2층 외벽/내벽 & 연결 계단(Stairs) 구축
    # -------------------------------------------------------------
    if use_2nd_floor:
        # A. 1층 ➔ 2층 연결 계단 (Stairs)
        stair_x = house_w * 0.35
        stair_y = house_l * 0.45
        stair_w = 1.2
        stair_l = 1.8
        stair_traces = create_stairs(stair_x, stair_y, 0, stair_w, stair_l, house_h, num_steps=10, color="#8D6E63", name="🪜 1층-2층 연결 계단")
        for trace in stair_traces:
            fig.add_trace(trace)
        fig.add_trace(go.Scatter3d(
            x=[stair_x + stair_w/2], y=[stair_y + stair_l/2], z=[house_h * 0.6],
            text=["<b>🪜 1층-2층 연결 계단</b>"], mode="text", showlegend=False, hoverinfo="text"
        ))

        # B. 2층 외벽 및 창문 (z = house_h)
        z2 = house_h
        fig.add_trace(create_3d_box(0, 0, z2, house_w*0.3, wall_th, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(house_w*0.3, 0, z2 + win_h_start, house_w*0.4, wall_th, win_h, "#81D4FA", "2층 전면 창문", opacity=0.5))
        fig.add_trace(create_3d_box(house_w*0.7, 0, z2, house_w*0.3, wall_th, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(0, 0, z2, wall_th, house_l, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(house_w - wall_th, 0, z2, wall_th, house_l, house_h*0.85, "#546E7A", "2층 외벽"))
        fig.add_trace(create_3d_box(0, house_l - wall_th, z2, house_w, wall_th, house_h*0.85, "#546E7A", "2층 후면 외벽"))

        # C. 2층 내벽
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

    # [출력 3] 종합 건축 분석
    st.subheader("💡 5. 건축 공간 및 복층(2층) 확장 가이드")
    st.write("• **치수 확장성**: 집 가로/세로 입력을 **최대 100m까지 제한 없이 자유롭게 지정**할 수 있습니다.")
    st.write("• **복층 구조 스위치**: '🏢 2층(복층) 구조 활성화' 체크박스로 2층 공간, 바닥 플레이트, 외벽, 연결 계단(🪜)을 켜고 끌 수 있습니다.")

except ValueError:
    st.error("❌ 올바른 숫자를 입력해 주세요.")
except Exception as e:
    st.error(f"❌ 오류 발생: {e}")
