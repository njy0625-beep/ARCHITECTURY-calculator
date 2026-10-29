import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 전체 주택 공간 & 가구 수직 적치 진단기", page_icon="🏠", layout="wide")

st.title("🏠 AI 기반 3D 전체 주택 & 가구 수직 적치(Stacking) 진단기")
st.caption("방 및 집 전체 공간에서 **책상 위 모니터, 서랍장 위 액자/화분 등 가구 위에 다른 가구를 올리는 수직 적치**까지 3D로 완벽히 시각화합니다.")

st.divider()

# -------------------------------------------------------------
# 2. 3D 입체 도형 생성 함수
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
    # [입력 1] 전체 집 구조 설정
    st.subheader("1. 집 전체 치수 및 공간 설정")
    col_hw, col_hl, col_hh = st.columns(3)
    with col_hw:
        house_w = st.number_input("집 전체 가로 (m):", min_value=3.0, max_value=30.0, value=8.0, step=0.5)
    with col_hl:
        house_l = st.number_input("집 전체 세로 (m):", min_value=3.0, max_value=30.0, value=6.0, step=0.5)
    with col_hh:
        house_h = st.number_input("천장 높이 (m):", min_value=1.5, max_value=5.0, value=2.4, step=0.1)

    if house_w <= 0 or house_l <= 0 or house_h <= 0:
        st.warning("⚠️ 치수는 모두 0보다 커야 합니다.")
        st.stop()

    total_house_area = house_w * house_l
    st.info(f"🏡 전체 집 면적: **{total_house_area:.2f} m²** | 천장 높이: **{house_h:.1f} m**")

    # 주택 4분할 구획 정의
    rooms_definition = {
        "거실 (Living Room)": {"x0": 0, "y0": 0, "w": house_w*0.6, "l": house_l*0.5, "color": "#EAEAEA"},
        "안방 (Master Bedroom)": {"x0": house_w*0.6, "y0": 0, "w": house_w*0.4, "l": house_l*0.5, "color": "#F3E5F5"},
        "작은방 (Bedroom 2)": {"x0": 0, "y0": house_l*0.5, "w": house_w*0.5, "l": house_l*0.5, "color": "#E1F5FE"},
        "주방/식당 (Kitchen)": {"x0": house_w*0.5, "y0": house_l*0.5, "w": house_w*0.5, "l": house_l*0.5, "color": "#FFF3E0"}
    }

    st.divider()

    # [입력 2] 가구 및 수직 적치(가구 위 올리기) 등록
    st.subheader("2. 커스텀 가구 & 가구 위 올리기(수직 적치) 설정")
    st.caption("💡 가구/소품 등록 시 **'배치 위치'**에서 기존 가구(책상, TV장 등)를 선택하면 그 위에 자동으로 올려집니다!")

    if "custom_items" not in st.session_state:
        st.session_state.custom_items = [
            {"name": "킹 침대", "room": "안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.6, "l": 2.1, "h": 0.5, "color": "#357ABD"},
            {"name": "1인용 책상", "room": "작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.2, "l": 0.7, "h": 0.75, "color": "#50E3C2"},
            {"name": "데스크탑 모니터", "room": "작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "1인용 책상", "w": 0.5, "l": 0.2, "h": 0.4, "color": "#212121"},
            {"name": "거실 소파", "room": "거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 2.2, "l": 0.9, "h": 0.8, "color": "#4A90E2"},
            {"name": "대형 TV장", "room": "거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "w": 1.8, "l": 0.4, "h": 0.5, "color": "#8D6E63"},
            {"name": "65인치 TV", "room": "거실 (Living Room)", "type": "일반 가구", "base_item": "대형 TV장", "w": 1.4, "l": 0.15, "h": 0.8, "color": "#000000"},
            {"name": "거실 페르시안 러그", "room": "거실 (Living Room)", "type": "러그/카페트 (바닥)", "base_item": "바닥 (z=0)", "w": 2.0, "l": 1.5, "h": 0.02, "color": "#FFAB91"},
            {"name": "벽걸이 유화 액자", "room": "거실 (Living Room)", "type": "벽걸이 액자 (벽면)", "base_item": "바닥 (z=0)", "w": 1.2, "l": 0.1, "h": 0.8, "color": "#FFD54F"}
        ]

    # 올려놓기 대상 가구 리스트 생성
    existing_furniture_names = ["바닥 (z=0)"] + [item["name"] for item in st.session_state.custom_items if item["type"] == "일반 가구"]

    with st.expander("➕ 새 가구/소품 등록 (가구 위 올려놓기 선택 기능)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name = st.text_input("아이템 이름:", value="탁상 조명")
            new_room = st.selectbox("배치할 방 선택:", options=list(rooms_definition.keys()))
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
            st.success(f"'{new_name}' 항목이 [{new_base}] 위에 등록되었습니다!")
            st.rerun()

    st.markdown("##### 📋 현재 등록된 가구 및 올려놓기(적치) 현황")
    if st.session_state.custom_items:
        items_to_remove = []
        for idx, item in enumerate(st.session_state.custom_items):
            ic1, ic2, ic3, ic4 = st.columns([3, 3, 3, 1])
            base_str = f" ➔ 위치: [{item['base_item']}] 위" if item['base_item'] != "바닥 (z=0)" else ""
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
    st.subheader("📊 3. 주택 전체 및 가구 배치 진단")
    total_furniture_area = sum(item["w"] * item["l"] for item in st.session_state.custom_items if item["type"] == "일반 가구" and item["base_item"] == "바닥 (z=0)")
    occupancy_ratio = (total_furniture_area / total_house_area) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("전체 주택 면적", f"{total_house_area:.2f} m²")
    m2.metric("바닥 점유 가구 면적", f"{total_furniture_area:.2f} m²")
    m3.metric("바닥 공간 점유율", f"{occupancy_ratio:.1f} %")

    st.divider()

    # [출력 2] 3D 가구 위 가구 올리기 시각화
    st.subheader("🧊 4. 3D 수직 적치(Stacking) 가구 배치 도면")
    st.caption("💡 책상 위 모니터, TV장 위 TV처럼 가구 위에 올려진 소품이 높이($z$) 좌표 계산으로 3D 표시됩니다.")

    fig = go.Figure()

    # 1) 전체 집 바닥
    for room_name, rdata in rooms_definition.items():
        rx0, ry0, rw, rl = rdata["x0"], rdata["y0"], rdata["w"], rdata["l"]
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx0+rw, rx0+rw, rx0],
            y=[ry0, ry0, ry0+rl, ry0+rl],
            z=[0, 0, 0, 0],
            color=rdata["color"], opacity=0.6, name=room_name
        ))
        fig.add_trace(go.Scatter3d(
            x=[rx0 + rw/2], y=[ry0 + rl/2], z=[0.05],
            text=[f"<b>{room_name}</b>"], mode="text", showlegend=False, hoverinfo="text"
        ))

    # 2) 집 외곽선
    hw, hl, hh = house_w, house_l, house_h
    outer_x = [0, hw, hw, 0, 0, 0, hw, hw, 0, 0, hw, hw, hw, hw, 0, 0]
    outer_y = [0, 0, hl, hl, 0, 0, 0, hl, hl, 0, 0, 0, hl, hl, hl, hl]
    outer_z = [0, 0, 0, 0, 0, hh, hh, hh, hh, hh, 0, hh, hh, 0, 0, hh]

    fig.add_trace(go.Scatter3d(
        x=outer_x, y=outer_y, z=outer_z,
        mode='lines', line=dict(color='black', width=4), showlegend=False, hoverinfo='none'
    ))

    fig.add_trace(go.Scatter3d(
        x=[hw*0.6, hw*0.6, hw*0.6, hw*0.6], y=[0, hl*0.5, hl*0.5, 0], z=[0, 0, hh*0.8, hh*0.8],
        mode='lines', line=dict(color='gray', width=2, dash='dash'), showlegend=False
    ))
    fig.add_trace(go.Scatter3d(
        x=[0, hw], y=[hl*0.5, hl*0.5], z=[0, 0],
        mode='lines', line=dict(color='gray', width=2, dash='dash'), showlegend=False
    ))

    # 3) 가구 적치 3D 좌표 계산 및 생성
    placed_items_coords = {}
    room_offsets = {rname: {"cx": rdata["x0"] + 0.3, "cy": rdata["y0"] + 0.3} for rname, rdata in rooms_definition.items()}

    floor_items = [item for item in st.session_state.custom_items if item["base_item"] == "바닥 (z=0)"]
    stacked_items = [item for item in st.session_state.custom_items if item["base_item"] != "바닥 (z=0)"]

    # 1단계: 바닥 가구 배치
    for item in floor_items:
        rname = item["room"]
        itype = item["type"]
        w, l, h = item["w"], item["l"], item["h"]
        rinfo = rooms_definition[rname]
        rx0, ry0, rw, rl = rinfo["x0"], rinfo["y0"], rinfo["w"], rinfo["l"]

        if itype == "러그/카페트 (바닥)":
            x0 = rx0 + (rw - w) / 2
            y0 = ry0 + (rl - l) / 2
            z0 = 0.01
            h_actual = 0.02
        elif itype == "벽걸이 액자 (벽면)":
            x0 = rx0 + 0.1
            y0 = ry0 + rl - l - 0.05
            z0 = 1.3
            h_actual = h
        else:
            cx = room_offsets[rname]["cx"]
            cy = room_offsets[rname]["cy"]
            if cx + w <= rx0 + rw - 0.2 and cy + l <= ry0 + rl - 0.2:
                x0, y0 = cx, cy
                room_offsets[rname]["cx"] += (w + 0.2)
            else:
                room_offsets[rname]["cx"] = rx0 + 0.3
                room_offsets[rname]["cy"] += (l + 0.3)
                x0 = room_offsets[rname]["cx"]
                y0 = room_offsets[rname]["cy"]
            z0 = 0
            h_actual = h

        x0 = max(rx0 + 0.05, min(x0, rx0 + rw - w - 0.05))
        y0 = max(ry0 + 0.05, min(y0, ry0 + rl - l - 0.05))

        placed_items_coords[item["name"]] = (x0, y0, z0, w, l, h_actual)

        box_mesh = create_3d_box(x0, y0, z0, w, l, h_actual, item["color"], f"[{rname.split(' ')[0]}] {item['name']}")
        fig.add_trace(box_mesh)
        fig.add_trace(go.Scatter3d(
            x=[x0 + w/2], y=[y0 + l/2], z=[z0 + h_actual + 0.15],
            text=[f"<b>{item['name']}</b>"], mode="text", showlegend=False, hoverinfo="text"
        ))

    # 2단계: 가구 상단 올리기(Stacking) 처리
    for item in stacked_items:
        parent_name = item["base_item"]
        if parent_name in placed_items_coords:
            px0, py0, pz0, pw, pl, ph = placed_items_coords[parent_name]
            w, l, h = item["w"], item["l"], item["h"]

            # 부모 가구 중앙 상단에 올리기
            x0 = px0 + (pw - w) / 2
            y0 = py0 + (pl - l) / 2
            z0 = pz0 + ph  # 부모 가구의 높이만큼 z축 상승

            placed_items_coords[item["name"]] = (x0, y0, z0, w, l, h)

            box_mesh = create_3d_box(x0, y0, z0, w, l, h, item["color"], f"[{parent_name} 위] {item['name']}")
            fig.add_trace(box_mesh)
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
        width=850,
        height=650,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("💡 5. 건축학 수직 공간(Stacking) 가이드")
    st.write("• **수직 레이어링(Vertical Layering)**: 바닥 면적을 늘리지 않고 **가구 상부 공간($z$-axis)**을 활용하면 주거 실면적 쾌적도를 크게 높일 수 있습니다.")
    st.write("• **하중 및 안정성**: 책상 위 모니터/노트북, TV장 위 TV 등 적치 시 상부 가구의 무게중심을 중앙에 배치하는 것이 조형적으로 안정적입니다.")

except ValueError:
    st.error("❌ 올바른 숫자를 입력해 주세요.")
except Exception as e:
    st.error(f"❌ 오류 발생: {e}")
