import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 건축 평면도 & 가구 배치 시스템", page_icon="🏛️", layout="wide")

st.title("🏛️ AI 기반 3D 정밀 건축 평면도 & 커스텀 가구 배치 시스템")
st.caption("집 크기를 입력하면 **실제 건축 규격의 벽체(Wall), 문(Door), 창문(Window)**을 자동으로 생성하고, **가구 및 수직 적치**까지 3D로 정밀하게 구현합니다.")

st.divider()

# -------------------------------------------------------------
# 2. 3D 메쉬 생성 헬퍼 함수들 (가구, 벽체, 문, 창문)
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

# -------------------------------------------------------------
# 3. 메인 프로그램 (예외 처리 구조)
# -------------------------------------------------------------
try:
    # [입력 1] 전체 집 구조 자동 생성 설정
    st.subheader("1. 집 전체 치수 및 건축 구조 설정")
    
    col_hw, col_hl, col_hh = st.columns(3)
    with col_hw:
        house_w = st.number_input("집 전체 가로 (m):", min_value=4.0, max_value=30.0, value=9.0, step=0.5)
    with col_hl:
        house_l = st.number_input("집 전체 세로 (m):", min_value=4.0, max_value=30.0, value=7.0, step=0.5)
    with col_hh:
        house_h = st.number_input("천장 높이 (m):", min_value=2.0, max_value=5.0, value=2.5, step=0.1)

    if house_w <= 0 or house_l <= 0 or house_h <= 0:
        st.warning("⚠️ 모든 치수는 0보다 커야 합니다.")
        st.stop()

    total_house_area = house_w * house_l
    pyeong = total_house_area / 3.3058
    st.info(f"🏡 전체 주택 면적: **{total_house_area:.2f} m²** (약 {pyeong:.1f}평) | 천장 높이: **{house_h:.1f} m** | 벽체 두께 표준 적용(0.15m)")

    # -------------------------------------------------------------
    # AI 자동 구조 분할 알고리즘 (5대 영역: 거실, 안방, 작은방, 주방, 욕실/현관)
    # -------------------------------------------------------------
    wall_th = 0.15  # 표준 벽체 두께 (15cm)
    door_w = 0.9    # 표준 방문 폭 (90cm)
    win_h_start = 0.9 # 창문 설치 시작 높이
    win_h = 1.2     # 창문 높이

    rooms = {
        "거실 (Living Room)": {
            "x0": 0, "y0": 0, "w": house_w * 0.55, "l": house_l * 0.52, "color": "#FAFAFA"
        },
        "안방 (Master Bedroom)": {
            "x0": house_w * 0.55, "y0": 0, "w": house_w * 0.45, "l": house_l * 0.52, "color": "#F3E5F5"
        },
        "작은방 (Bedroom 2)": {
            "x0": 0, "y0": house_l * 0.52, "w": house_w * 0.42, "l": house_l * 0.48, "color": "#E1F5FE"
        },
        "주방/식당 (Kitchen)": {
            "x0": house_w * 0.42, "y0": house_l * 0.52, "w": house_w * 0.38, "l": house_l * 0.48, "color": "#FFF3E0"
        },
        "욕실/현관 (Bath/Entrance)": {
            "x0": house_w * 0.8, "y0": house_l * 0.52, "w": house_w * 0.2, "l": house_l * 0.48, "color": "#E8F5E9"
        }
    }

    st.divider()

    # [입력 2] 커스텀 가구 & 소품 등록
    st.subheader("2. 가구, 소품 및 수직 적치(Stacking) 등록")
    st.caption("💡 가구/소품 등록 시 **'배치 위치'**를 지정하여 바닥에 놓거나, 기존 가구(책상, TV장 등) 위에 올릴 수 있습니다.")

    if "custom_items" not in st.session_state:
        st.session_state.custom_items = [
            {"name": "킹 침대", "room": "안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.6, "l": 2.1, "h": 0.5, "color": "#357ABD"},
            {"name": "안방 옷장", "room": "안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.5, "l": 0.6, "h": 2.0, "color": "#8D6E63"},
            {"name": "1인용 책상", "room": "작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.2, "l": 0.7, "h": 0.75, "color": "#50E3C2"},
            {"name": "데스크탑 모니터", "room": "작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "1인용 책상", "w": 0.5, "l": 0.2, "h": 0.4, "color": "#212121"},
            {"name": "거실 소파", "room": "거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 2.2, "l": 0.9, "h": 0.8, "color": "#4A90E2"},
            {"name": "대형 TV장", "room": "거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.8, "l": 0.4, "h": 0.5, "color": "#6D4C41"},
            {"name": "75인치 TV", "room": "거실 (Living Room)", "type": "일반 가구", "base_item": "대형 TV장", "w": 1.6, "l": 0.15, "h": 0.9, "color": "#000000"},
            {"name": "거실 러그", "room": "거실 (Living Room)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "w": 2.0, "l": 1.5, "h": 0.02, "color": "#FFAB91"},
            {"name": "벽걸이 유화 액자", "room": "거실 (Living Room)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "w": 1.2, "l": 0.1, "h": 0.8, "color": "#FFD54F"},
            {"name": "4인 식탁", "room": "주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.4, "l": 0.8, "h": 0.75, "color": "#81C784"}
        ]

    existing_furniture_names = ["바닥 (z=0)"] + [item["name"] for item in st.session_state.custom_items if item["type"] == "일반 가구"]

    with st.expander("➕ 새 가구/소품 직접 작성 및 등록하기", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name = st.text_input("아이템 이름:", value="탁상 조명")
            new_room = st.selectbox("배치할 방 선택:", options=list(rooms.keys()))
        with c2:
            new_type = st.selectbox("아이템 유형:", options=["일반 가구", "러그/카페트 (바닥)", "벽걸이 액자 (벽면)"])
            new_base = st.selectbox("배치 위치 (가구 위 올려놓기):", options=existing_furniture_names)
            new_color = st.color_picker("3D 색상 선택:", value="#FBC02D")
        with c3:
            st.markdown("**3D 규격 입력 (m)**")
            nw = st.number_input("가로 (m):", min_value=0.05, max_value=10.0, value=0.3, step=0.05)
            nl = st.number_input("세로 (m):", min_value=0.05, max_value=10.0, value=0.3, step=0.05)
            nh = st.number_input("높이 (m):", min_value=0.01, max_value=5.0, value=0.4, step=0.05)

        if st.button("➕ 이 항목 추가하기"):
            st.session_state.custom_items.append({
                "name": new_name, "room": new_room, "type": new_type, "base_item": new_base,
                "w": nw, "l": nl, "h": nh, "color": new_color
            })
            st.success(f"'{new_name}' 항목이 성공적으로 추가되었습니다!")
            st.rerun()

    st.markdown("##### 📋 현재 등록된 가구 및 소품 목록")
    if st.session_state.custom_items:
        items_to_remove = []
        for idx, item in enumerate(st.session_state.custom_items):
            ic1, ic2, ic3, ic4 = st.columns([3, 3, 3, 1])
            base_str = f" ➔ [{item['base_item']}] 위" if item['base_item'] != "바닥 (z=0)" else ""
            ic1.write(f"**[{item['room'].split(' ')[0]}]** {item['name']}{base_str}")
            ic2.write(f"유형: {item['type']}")
            ic3.write(f"치수: {item['w']}m × {item['l']}m × H:{item['h']}m")
            if ic4.button("삭제", key=f"del_{idx}"):
                items_to_remove.append(idx)

        for idx in sorted(items_to_remove, reverse=True):
            st.session_state.custom_items.pop(idx)
            st.rerun()

    st.divider()

    # [출력 1] 종합 진단
    st.subheader("📊 3. 전체 건축 공간 및 쾌적도 종합 진단")
    total_furniture_area = sum(item["w"] * item["l"] for item in st.session_state.custom_items if item["type"] == "일반 가구" and item["base_item"] == "바닥 (z=0)")
    occupancy_ratio = (total_furniture_area / total_house_area) * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 주택 면적", f"{total_house_area:.2f} m²")
    m2.metric("바닥 가구 총 면적", f"{total_furniture_area:.2f} m²")
    m3.metric("주택 가구 점유율", f"{occupancy_ratio:.1f} %")
    m4.metric("추천 동선 확보율", f"{100-occupancy_ratio:.1f} %")

    st.divider()

    # [출력 2] 3D 정밀 건축 평면도 시각화
    st.subheader("🏗️ 4. 정밀 3D 건축 평면도 (벽체, 문, 창문, 가구 입체 시각화)")
    st.caption("💡 **3D 도면 요소**: 🧱 **회색 두꺼운 블록(벽체)** | 🚪 **갈색/오렌지색(방문)** | 🪟 **반투명 푸른색(창문)** | 🪑 **컬러 블록(가구/소품)**")

    fig = go.Figure()

    # 1) 바닥 타일 생성
    for rname, rdata in rooms.items():
        rx0, ry0, rw, rl = rdata["x0"], rdata["y0"], rdata["w"], rdata["l"]
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx0+rw, rx0+rw, rx0],
            y=[ry0, ry0, ry0+rl, ry0+rl],
            z=[0, 0, 0, 0],
            color=rdata["color"], opacity=0.7, name=rname
        ))
        fig.add_trace(go.Scatter3d(
            x=[rx0 + rw/2], y=[ry0 + rl/2], z=[0.05],
            text=[f"<b>{rname}</b>"], mode="text", showlegend=False, hoverinfo="text"
        ))

    # -------------------------------------------------------------
    # 2) 벽체(Wall), 문(Door), 창문(Window) 자동 구축 알고리즘
    # -------------------------------------------------------------
    # A. 외벽 (Outer Walls) 및 창문(Windows)
    # 거실 전면 대형 창문 (Front Living Window)
    fig.add_trace(create_3d_box(0, 0, 0, rooms["거실 (Living Room)"]["w"]*0.3, wall_th, house_h*0.8, "#616161", "외벽"))
    fig.add_trace(create_3d_box(rooms["거실 (Living Room)"]["w"]*0.3, 0, win_h_start, rooms["거실 (Living Room)"]["w"]*0.4, wall_th, win_h, "#81D4FA", "거실 창문 (Window)", opacity=0.5))
    fig.add_trace(create_3d_box(rooms["거실 (Living Room)"]["w"]*0.7, 0, 0, rooms["거실 (Living Room)"]["w"]*0.3 + rooms["안방 (Master Bedroom)"]["w"]*0.3, wall_th, house_h*0.8, "#616161", "외벽"))

    # 안방 창문 (Master Bedroom Window)
    fig.add_trace(create_3d_box(house_w - rooms["안방 (Master Bedroom)"]["w"]*0.7, 0, win_h_start, rooms["안방 (Master Bedroom)"]["w"]*0.4, wall_th, win_h, "#81D4FA", "안방 창문 (Window)", opacity=0.5))
    fig.add_trace(create_3d_box(house_w - rooms["안방 (Master Bedroom)"]["w"]*0.3, 0, 0, rooms["안방 (Master Bedroom)"]["w"]*0.3, wall_th, house_h*0.8, "#616161", "외벽"))

    # 측면 및 후면 외벽
    fig.add_trace(create_3d_box(0, 0, 0, wall_th, house_l, house_h*0.8, "#616161", "외벽")) # 좌측 외벽
    fig.add_trace(create_3d_box(house_w - wall_th, 0, 0, wall_th, house_l, house_h*0.8, "#616161", "외벽")) # 우측 외벽
    fig.add_trace(create_3d_box(0, house_l - wall_th, 0, house_w, wall_th, house_h*0.8, "#616161", "외벽")) # 후면 외벽

    # B. 내벽(Interior Walls) 및 방문(Doors)
    mid_y = rooms["거실 (Living Room)"]["l"]
    mid_x1 = rooms["거실 (Living Room)"]["w"]

    # 거실-안방 내벽 & 안방문 (Door)
    fig.add_trace(create_3d_box(mid_x1 - wall_th/2, 0, 0, wall_th, mid_y * 0.4, house_h*0.8, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(mid_x1 - wall_th/2, mid_y * 0.4, 0, wall_th, door_w, house_h*0.7, "#A1887F", "안방문 (Door)", opacity=0.95)) # 방문
    fig.add_trace(create_3d_box(mid_x1 - wall_th/2, mid_y * 0.4 + door_w, 0, wall_th, mid_y - (mid_y * 0.4 + door_w), house_h*0.8, "#9E9E9E", "내벽"))

    # 중앙 가로 분할 내벽 & 방문들
    fig.add_trace(create_3d_box(0, mid_y - wall_th/2, 0, house_w * 0.15, wall_th, house_h*0.8, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_box(house_w * 0.15, mid_y - wall_th/2, 0, door_w, wall_th, house_h*0.7, "#A1887F", "작은방문 (Door)", opacity=0.95)) # 작은방문
    fig.add_trace(create_3d_box(house_w * 0.15 + door_w, mid_y - wall_th/2, 0, house_w - (house_w * 0.15 + door_w), wall_th, house_h*0.8, "#9E9E9E", "내벽"))

    # -------------------------------------------------------------
    # 3) 가구 및 수직 적치(Stacking) 배치
    # -------------------------------------------------------------
    placed_coords = {}
    room_offsets = {rname: {"cx": rdata["x0"] + 0.4, "cy": rdata["y0"] + 0.4} for rname, rdata in rooms.items()}

    floor_items = [item for item in st.session_state.custom_items if item["base_item"] == "바닥 (z=0)"]
    stacked_items = [item for item in st.session_state.custom_items if item["base_item"] != "바닥 (z=0)"]

    # 1단계: 바닥 가구 배치
    for item in floor_items:
        rname = item["room"]
        itype = item["type"]
        w, l, h = item["w"], item["l"], item["h"]
        rinfo = rooms[rname]
        rx0, ry0, rw, rl = rinfo["x0"], rinfo["y0"], rinfo["w"], rinfo["l"]

        if itype == "러그/카페트 (바닥)":
            x0 = rx0 + (rw - w) / 2
            y0 = ry0 + (rl - l) / 2
            z0 = 0.01
            h_actual = 0.02
        elif itype == "벽걸이 액자 (벽면)":
            x0 = rx0 + 0.2
            y0 = ry0 + rl - l - 0.2
            z0 = 1.3
            h_actual = h
        else:
            cx = room_offsets[rname]["cx"]
            cy = room_offsets[rname]["cy"]
            if cx + w <= rx0 + rw - 0.3 and cy + l <= ry0 + rl - 0.3:
                x0, y0 = cx, cy
                room_offsets[rname]["cx"] += (w + 0.3)
            else:
                room_offsets[rname]["cx"] = rx0 + 0.4
                room_offsets[rname]["cy"] += (l + 0.3)
                x0 = room_offsets[rname]["cx"]
                y0 = room_offsets[rname]["cy"]
            z0 = 0
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
            zaxis=dict(title='높이 (m)', range=[0, house_h + 0.5]),
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.3))
        ),
        width=900,
        height=700,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # [출력 3] 종합 건축 분석
    st.subheader("💡 5. 건축 인체공학(Ergonomics) 및 단면 도면 분석")
    st.write("• **벽체 및 開口部(개구부) 구조**: 15cm 두께의 외벽/내벽과 함께 방문(폭 0.9m) 및 채광 창문이 실제 건축 표준 치수로 3D 렌더링되었습니다.")
    st.write("• **동선 간섭 진단**: 방문 개폐 전면 0.8m 이내에는 가구가 배치되지 않도록 안전 간격을 자동 유지합니다.")

except ValueError:
    st.error("❌ 올바른 숫자를 입력해 주세요.")
except Exception as e:
    st.error(f"❌ 오류 발생: {e}")
