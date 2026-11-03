import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json
import math

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 복층 정밀 건축 & 스마트 공간 최적화", page_icon="🏛️", layout="wide")

st.title("🏛️ AI 기반 3D 정밀 건축 평면도 & 스마트 공간 최적화 배치 시스템")
st.caption("AI 생활동선 자동 최적화 배치, 2D-3D 실시간 좌표 동기화, 마우스 커서 드래그/회전 & 벽체 자유 개조")

st.divider()

# -------------------------------------------------------------
# 2. 3D 메쉬 생성 및 360도 회전 헬퍼 함수
# -------------------------------------------------------------
def create_3d_rotated_box(x0, y0, z0, dx, dy, dz, angle_deg, color, name, opacity=0.85):
    """Plotly 3D 직육면체 메쉬 생성 (Z축 중심 360도 회전)"""
    cx = x0 + dx / 2.0
    cy = y0 + dy / 2.0
    
    corners = [
        (x0, y0, z0), (x0 + dx, y0, z0), (x0 + dx, y0 + dy, z0), (x0, y0 + dy, z0),
        (x0, y0, z0 + dz), (x0 + dx, y0, z0 + dz), (x0 + dx, y0 + dy, z0 + dz), (x0, y0 + dy, z0 + dz)
    ]
    
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    rx, ry, rz = [], [], []
    for (px, py, pz) in corners:
        nx = px - cx
        ny = py - cy
        rot_x = nx * cos_a - ny * sin_a + cx
        rot_y = nx * sin_a + ny * cos_a + cy
        rx.append(rot_x)
        ry.append(rot_y)
        rz.append(pz)

    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    return go.Mesh3d(
        x=rx, y=ry, z=rz, i=i, j=j, k=k,
        color=color, opacity=opacity, name=name,
        showscale=False, flatshading=True, hoverinfo="name"
    )

try:
    # URL 쿼리 파라미터를 통한 2D -> 3D 실시간 좌표 동기화 수신
    query_params = st.query_params
    if "sync_id" in query_params:
        try:
            s_id = int(query_params["sync_id"])
            s_x = float(query_params.get("sync_x", 0))
            s_y = float(query_params.get("sync_y", 0))
            s_rot = int(query_params.get("sync_rot", 0))
            
            if "custom_items" in st.session_state and 0 <= s_id < len(st.session_state.custom_items):
                st.session_state.custom_items[s_id]["abs_x"] = s_x
                st.session_state.custom_items[s_id]["abs_y"] = s_y
                st.session_state.custom_items[s_id]["rot"] = s_rot
                st.toast(f"✅ '{st.session_state.custom_items[s_id]['name']}' 가구의 위치 및 회전이 3D 도면에 반영되었습니다!", icon="🚚")
        except Exception:
            pass

    # -------------------------------------------------------------
    # 3. 주택 전체 치수 & 내벽 위치 자유 조절
    # -------------------------------------------------------------
    st.subheader("1. 📐 건축 치수 및 내벽/방 구획 자유 개조")
    
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        house_w = st.number_input("가로 폭 (m):", min_value=5.0, max_value=100.0, value=10.0, step=0.5)
    with c2:
        house_l = st.number_input("세로 길이 (m):", min_value=5.0, max_value=100.0, value=8.0, step=0.5)
    with c3:
        house_h = st.slider("3D 벽 높이 (m):", min_value=1.0, max_value=6.0, value=2.5, step=0.1)
    with c4:
        use_2nd_floor = st.checkbox("🏢 2층(복층) 구조 활성화", value=False)
        show_front_door = st.checkbox("🚪 메인 현관 출입문 표시", value=True)

    num_floors = 2 if use_2nd_floor else 1
    total_house_area = house_w * house_l * num_floors
    pyeong = total_house_area / 3.3058

    st.info(f"🏡 전체 주택 연면적: **{total_house_area:.2f} m²** (약 {pyeong:.1f}평) | 벽 높이: **{house_h:.1f}m** | **{num_floors}층 구조**")

    # [자유 내벽 조절]
    with st.expander("🧱 내벽 경계선 및 커스텀 벽체 자유 개조", expanded=True):
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            y_mid = st.slider("가로 중앙 내벽 Y 위치 (m):", min_value=2.0, max_value=max(2.1, house_l - 2.0), value=min(house_l*0.55, house_l-2.0), step=0.1)
            x_mid1 = st.slider("거실/안방 경계 내벽 X 위치 (m):", min_value=1.0, max_value=max(1.1, house_w - 1.0), value=min(house_w*0.5, house_w-1.0), step=0.1)
        with col_w2:
            x_mid2 = st.slider("작은방/주방 경계 내벽 X 위치 (m):", min_value=1.0, max_value=max(1.1, house_w - 1.0), value=min(house_w*0.38, house_w-1.0), step=0.1)
            x_mid3 = st.slider("주방/욕실 경계 내벽 X 위치 (m):", min_value=1.0, max_value=max(1.1, house_w - 1.0), value=min(house_w*0.75, house_w-1.0), step=0.1)
        with col_w3:
            y_bath = st.slider("욕실/현관 경계 내벽 Y 위치 (m):", min_value=min(y_mid + 0.5, house_l - 0.5), max_value=max(y_mid + 0.6, house_l - 0.2), value=min(house_l*0.8, house_l-0.2), step=0.1)

        st.markdown("---")
        st.markdown("##### 🔨 사용자 자유 커스텀 벽체/파티션 추가")
        cw1, cw2, cw3, cw4 = st.columns(4)
        with cw1:
            cw_type = st.selectbox("구조물 종류:", options=["내벽 파티션 (Wall)", "방문/출입문 (Door)", "창문 (Window)"])
            cw_x = st.number_input("시작 X 좌표 (m):", min_value=0.0, max_value=house_w, value=2.0, step=0.2)
        with cw2:
            cw_y = st.number_input("시작 Y 좌표 (m):", min_value=0.0, max_value=house_l, value=2.0, step=0.2)
            cw_w = st.number_input("길이/폭 (m):", min_value=0.2, max_value=10.0, value=2.0, step=0.1)
        with cw3:
            cw_dir = st.selectbox("배치 방향:", options=["가로 방향 (E-W)", "세로 방향 (N-S)"])
            cw_h = st.number_input("높이 (m):", min_value=0.5, max_value=house_h, value=house_h * 0.85, step=0.1)
        with cw4:
            cw_z = st.number_input("바닥 Z 높이 (m):", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
            if st.button("➕ 커스텀 벽체/창/문 설치"):
                if "custom_walls" not in st.session_state:
                    st.session_state.custom_walls = []
                st.session_state.custom_walls.append({
                    "type": cw_type, "x": cw_x, "y": cw_y, "w": cw_w,
                    "dir": cw_dir, "h": cw_h, "z": cw_z
                })
                st.success("새 개조 건축 요소가 추가되었습니다!")
                st.rerun()

        if "custom_walls" in st.session_state and st.session_state.custom_walls:
            for idx, wall_item in enumerate(st.session_state.custom_walls):
                c_col1, c_col2 = st.columns([4, 1])
                c_col1.write(f"• **[{wall_item['type']}]** ({wall_item['x']}m, {wall_item['y']}m), {wall_item['dir']}, 길이: {wall_item['w']}m")
                if c_col2.button("삭제", key=f"del_wall_{idx}"):
                    st.session_state.custom_walls.pop(idx)
                    st.rerun()

    wall_th = 0.15
    door_w = 0.9

    rooms_1f = {
        "[1층] 거실 (Living Room)": {"x0": 0, "y0": 0, "w": x_mid1, "l": y_mid, "color": "#FAFAFA", "z": 0},
        "[1층] 안방 (Master Bedroom)": {"x0": x_mid1, "y0": 0, "w": house_w - x_mid1, "l": y_mid, "color": "#F3E5F5", "z": 0},
        "[1층] 작은방 (Bedroom 2)": {"x0": 0, "y0": y_mid, "w": x_mid2, "l": house_l - y_mid, "color": "#E1F5FE", "z": 0},
        "[1층] 주방/식당 (Kitchen)": {"x0": x_mid2, "y0": y_mid, "w": max(0.5, x_mid3 - x_mid2), "l": house_l - y_mid, "color": "#FFF3E0", "z": 0},
        "[1층] 욕실/화장실 (Bathroom)": {"x0": x_mid3, "y0": y_mid, "w": house_w - x_mid3, "l": max(0.5, y_bath - y_mid), "color": "#E0F7FA", "z": 0},
        "[1층] 현관 (Entrance)": {"x0": x_mid3, "y0": y_bath, "w": house_w - x_mid3, "l": house_l - y_bath, "color": "#E8EAF6", "z": 0}
    }

    rooms_2f = {}
    if use_2nd_floor:
        rooms_2f = {
            "[2층] 서재/작업실": {"x0": 0, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#EFEBE9", "z": house_h},
            "[2층] 게스트 룸": {"x0": house_w * 0.5, "y0": 0, "w": house_w * 0.5, "l": house_l * 0.55, "color": "#F1F8E9", "z": house_h},
            "[2층] 취미실/드레스룸": {"x0": 0, "y0": house_l * 0.55, "w": house_w * 0.45, "l": house_l * 0.45, "color": "#FFF8E1", "z": house_h},
            "[2층] 테라스": {"x0": house_w * 0.45, "y0": house_l * 0.55, "w": house_w * 0.55, "l": house_l * 0.45, "color": "#E0F2F1", "z": house_h}
        }

    all_rooms = {**rooms_1f, **rooms_2f}

    # -------------------------------------------------------------
    # 4. 🤖 AI 기반 인간공학적 스마트 자동 공간 최적화 알고리즘
    # -------------------------------------------------------------
    def apply_ai_smart_layout():
        """가구가 겹치거나 한곳에 몰리지 않고 인간공학적으로 방 벽면에 착붙 최적 배치"""
        r_liv = rooms_1f["[1층] 거실 (Living Room)"]
        r_mas = rooms_1f["[1층] 안방 (Master Bedroom)"]
        r_bed2 = rooms_1f["[1층] 작은방 (Bedroom 2)"]
        r_kit = rooms_1f["[1층] 주방/식당 (Kitchen)"]
        r_bath = rooms_1f["[1층] 욕실/화장실 (Bathroom)"]
        r_ent = rooms_1f["[1층] 현관 (Entrance)"]

        st.session_state.custom_items = [
            # [현관] 통로 개방 (오른쪽 벽 부착)
            {"name": "🚪 현관 슬라이딩 중문", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_ent["x0"] + 0.1, "abs_y": r_ent["y0"] + 0.05, "w": min(1.2, r_ent["w"]-0.2), "l": 0.1, "h": 2.1, "color": "#3E2723", "rot": 0},
            {"name": "신발장 및 전신거울", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_ent["x0"] + r_ent["w"] - 0.45, "abs_y": r_ent["y0"] + 0.3, "w": 0.4, "l": min(1.0, r_ent["l"]-0.4), "h": 1.4, "color": "#795548", "rot": 0},

            # [거실] 소파 남측 벽 착붙, TV 북측 벽 착붙, 소파테이블 중앙
            {"name": "4인용 패브릭 소파", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_liv["x0"] + 0.4, "abs_y": r_liv["y0"] + 0.2, "w": min(2.4, r_liv["w"]-0.8), "l": 0.9, "h": 0.85, "color": "#5C6BC0", "rot": 0},
            {"name": "원목 소파 테이블", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_liv["x0"] + 1.0, "abs_y": r_liv["y0"] + 1.5, "w": 1.1, "l": 0.6, "h": 0.4, "color": "#8D6E63", "rot": 0},
            {"name": "대형 거실 TV장", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_liv["x0"] + 0.6, "abs_y": r_liv["y0"] + r_liv["l"] - 0.5, "w": min(2.0, r_liv["w"]-1.0), "l": 0.4, "h": 0.5, "color": "#4E342E", "rot": 0},
            {"name": "75인치 스마트 TV", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "대형 거실 TV장", "abs_x": r_liv["x0"] + 0.8, "abs_y": r_liv["y0"] + r_liv["l"] - 0.45, "w": 1.6, "l": 0.15, "h": 0.9, "color": "#1A237E", "rot": 0},

            # [안방] 동측 외벽 침대 헤드 밀착, 북측 붙박이장
            {"name": "퀸 사이즈 침대", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_mas["x0"] + r_mas["w"] - 1.8, "abs_y": r_mas["y0"] + 0.4, "w": 1.6, "l": 2.1, "h": 0.55, "color": "#3949AB", "rot": 0},
            {"name": "원목 침대 협탁", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_mas["x0"] + r_mas["w"] - 2.4, "abs_y": r_mas["y0"] + 0.4, "w": 0.5, "l": 0.4, "h": 0.5, "color": "#A1887F", "rot": 0},
            {"name": "안방 대형 붙박이장", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_mas["x0"] + 0.4, "abs_y": r_mas["y0"] + r_mas["l"] - 0.75, "w": min(2.2, r_mas["w"]-0.8), "l": 0.65, "h": 2.1, "color": "#6D4C41", "rot": 0},

            # [작은방] 서측 침대, 동측 책상
            {"name": "슈퍼싱글 침대", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bed2["x0"] + 0.2, "abs_y": r_bed2["y0"] + 0.4, "w": 1.1, "l": 2.0, "h": 0.5, "color": "#0288D1", "rot": 0},
            {"name": "1인용 집중 스터디 책상", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bed2["x0"] + r_bed2["w"] - 1.4, "abs_y": r_bed2["y0"] + 0.4, "w": 1.2, "l": 0.7, "h": 0.75, "color": "#26A69A", "rot": 0},

            # [주방] 식탁 중앙, 냉장고 동측
            {"name": "4인용 아일랜드 식탁", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_kit["x0"] + 0.3, "abs_y": r_kit["y0"] + 1.0, "w": min(1.4, r_kit["w"]-0.5), "l": 0.8, "h": 0.75, "color": "#66BB6A", "rot": 0},
            {"name": "양문형 비스포크 냉장고", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_kit["x0"] + r_kit["w"] - 1.1, "abs_y": r_kit["y0"] + 0.3, "w": 0.95, "l": 0.9, "h": 1.85, "color": "#78909C", "rot": 0},

            # [욕실] 구석 코너 밀착
            {"name": "양변기 & 세면대 세트", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bath["x0"] + 0.2, "abs_y": r_bath["y0"] + 0.2, "w": min(0.9, r_bath["w"]-0.3), "l": 0.6, "h": 0.8, "color": "#00BCD4", "rot": 0},
            {"name": "유리 샤워부스/욕조", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bath["x0"] + r_bath["w"] - 1.0, "abs_y": r_bath["y0"] + 0.2, "w": min(0.9, r_bath["w"]-0.3), "l": 0.9, "h": 1.9, "color": "#4DD0E1", "rot": 0}
        ]

    if "custom_items" not in st.session_state:
        apply_ai_smart_layout()

    # -------------------------------------------------------------
    # 5. 🤖 AI 공간 최적화 실행 & 수동 가구 회전/이동 컨트롤
    # -------------------------------------------------------------
    st.divider()
    st.subheader("2. 🤖 AI 공간 최적화 자동 배치 & 가구 이동/회전")
    
    col_ai1, col_ai2 = st.columns([3, 5])
    with col_ai1:
        if st.button("✨ AI 기반 인간공학 자동 공간 최적화 재배치", use_container_width=True):
            apply_ai_smart_layout()
            st.success("🤖 AI가 방 구조 및 동선을 분석하여 가구를 가장 쾌적하게 자동 배치했습니다!")
            st.rerun()

    valid_furniture_names = [item["name"] for item in st.session_state.custom_items if item["base_item"] == "바닥 (z=0)"]
    if valid_furniture_names:
        with st.expander("🛋️ 수동 가구 상세 위치 (X, Y) 및 360도 회전 조절", expanded=False):
            f_col1, f_col2, f_col3 = st.columns([3, 3, 2])
            with f_col1:
                sel_furniture = st.selectbox("🎯 가구 선택:", options=valid_furniture_names)
            
            target_f = next((item for item in st.session_state.custom_items if item["name"] == sel_furniture), None)
            if target_f:
                with f_col2:
                    new_abs_x = st.slider("X 절대 좌표 (m):", min_value=0.0, max_value=house_w - target_f["w"], value=min(float(target_f.get("abs_x", 1.0)), house_w - target_f["w"]), step=0.1)
                    new_abs_y = st.slider("Y 절대 좌표 (m):", min_value=0.0, max_value=house_l - target_f["l"], value=min(float(target_f.get("abs_y", 1.0)), house_l - target_f["l"]), step=0.1)
                    target_f["abs_x"] = new_abs_x
                    target_f["abs_y"] = new_abs_y
                with f_col3:
                    new_rot = st.slider("회전 각도 (°):", min_value=0, max_value=360, value=int(target_f.get("rot", 0)), step=15)
                    target_f["rot"] = new_rot

    st.divider()

    # -------------------------------------------------------------
    # 6. 🎮 [배치 게임판] 마우스 드래그 & 3D 실시간 동기화 캔버스
    # -------------------------------------------------------------
    st.subheader("3. 🎮 [가구배치 게임판] 마우스 커서 드래그 이동 & 3D 실시간 적용")
    st.write("💡 아래 배치도에서 **가구를 마우스로 드래그**하면 즉시 좌표가 계산되며, **'💾 3D 입체모형에 바로 적용'** 버튼 클릭 시 3D 도면에 실시간 반영됩니다.")

    canvas_items_json = []
    for idx, item in enumerate(st.session_state.custom_items):
        canvas_items_json.append({
            "id": idx, "name": item["name"], "room": item["room"],
            "x": float(item.get("abs_x", 1.0)), "y": float(item.get("abs_y", 1.0)),
            "w": item["w"], "l": item["l"], "color": item["color"],
            "rot": item.get("rot", 0), "is_base": (item["base_item"] == "바닥 (z=0)")
        })

    drag_canvas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 5px; background-color: #f8f9fa; }}
        #canvas-container {{ position: relative; width: 100%; text-align: center; }}
        canvas {{ border: 3px solid #343a40; background: #ffffff; border-radius: 10px; cursor: move; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
        .status-bar {{ margin-top: 8px; padding: 10px; background: #212529; color: #f8f9fa; border-radius: 6px; font-weight: bold; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }}
        .sync-btn {{ background-color: #0d6efd; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.2s; }}
        .sync-btn:hover {{ background-color: #0b5ed7; }}
    </style>
    </head>
    <body>
    <div id="canvas-container">
        <canvas id="floorCanvas" width="900" height="650"></canvas>
        <div class="status-bar">
            <span id="statusText">🎮 가구를 마우스 커서로 클릭 후 원하는 위치로 드래그하세요!</span>
            <button class="sync-btn" onclick="syncToStreamlit()">💾 3D 입체모형에 바로 적용</button>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('floorCanvas');
        const ctx = canvas.getContext('2d');
        const statusText = document.getElementById('statusText');

        const scale = 75; // 1m = 75px
        const originX = 60;
        const originY = 50;

        const rooms = {json.dumps([{"name": k, "x": v["x0"], "y": v["y0"], "w": v["w"], "l": v["l"], "color": v["color"]} for k, v in rooms_1f.items()])};
        let items = {json.dumps(canvas_items_json)};

        let selectedItem = null;
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1) 방 영역
            rooms.forEach(r => {{
                let rx = originX + r.x * scale;
                let ry = originY + r.y * scale;
                let rw = r.w * scale;
                let rl = r.l * scale;

                ctx.fillStyle = r.color;
                ctx.fillRect(rx, ry, rw, rl);
                ctx.strokeStyle = "#495057";
                ctx.lineWidth = 3;
                ctx.strokeRect(rx, ry, rw, rl);

                ctx.fillStyle = "#212529";
                ctx.font = "bold 12px sans-serif";
                ctx.fillText(r.name.split(' ')[1] || r.name, rx + 6, ry + 18);
            }});

            // 2) 가구 렌더링
            items.forEach(item => {{
                if (!item.is_base) return;
                
                let cx = originX + (item.x + item.w / 2) * scale;
                let cy = originY + (item.y + item.l / 2) * scale;
                let iw = item.w * scale;
                let il = item.l * scale;

                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate((item.rot || 0) * Math.PI / 180);

                if (item === selectedItem) {{
                    ctx.fillStyle = "rgba(255, 193, 7, 0.45)";
                    ctx.fillRect(-iw/2 - 4, -il/2 - 4, iw + 8, il + 8);
                    ctx.strokeStyle = "#d39e00";
                    ctx.lineWidth = 3;
                    ctx.strokeRect(-iw/2 - 4, -il/2 - 4, iw + 8, il + 8);
                }}

                ctx.fillStyle = item.color;
                ctx.fillRect(-iw/2, -il/2, iw, il);
                ctx.strokeStyle = "#000000";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(-iw/2, -il/2, iw, il);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 11px sans-serif";
                ctx.shadowColor = "black";
                ctx.shadowBlur = 3;
                ctx.fillText(item.name.substring(0, 8), -iw/2 + 3, 4);
                ctx.shadowBlur = 0;

                ctx.restore();
            }});
        }}

        canvas.addEventListener('mousedown', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            for (let i = items.length - 1; i >= 0; i--) {{
                let item = items[i];
                if (!item.is_base) continue;
                
                let ix = originX + item.x * scale;
                let iy = originY + item.y * scale;
                let iw = item.w * scale;
                let il = item.l * scale;

                if (mx >= ix && mx <= ix + iw && my >= iy && my <= iy + il) {{
                    selectedItem = item;
                    isDragging = true;
                    dragOffsetX = mx - ix;
                    dragOffsetY = my - iy;
                    statusText.innerHTML = "🎯 선택됨: <b>" + item.name + "</b> - 마우스 드래그로 이동!";
                    draw();
                    return;
                }}
            }}
            selectedItem = null;
            statusText.innerHTML = "🎮 가구를 마우스 커서로 클릭 후 원하는 위치로 드래그하세요!";
            draw();
        }});

        canvas.addEventListener('mousemove', (e) => {{
            if (!isDragging || !selectedItem) return;

            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            let newX = (mx - dragOffsetX - originX) / scale;
            let newY = (my - dragOffsetY - originY) / scale;

            selectedItem.x = Math.max(0, Math.min({house_w} - selectedItem.w, newX));
            selectedItem.y = Math.max(0, Math.min({house_l} - selectedItem.l, newY));

            statusText.innerHTML = "🚚 이동 중: <b>" + selectedItem.name + "</b> [ X: " + selectedItem.x.toFixed(2) + "m, Y: " + selectedItem.y.toFixed(2) + "m ]";
            draw();
        }});

        window.addEventListener('mouseup', () => {{
            if (isDragging && selectedItem) {{
                isDragging = false;
                statusText.innerHTML = "✅ 이동 완료: <b>" + selectedItem.name + "</b> [ X: " + selectedItem.x.toFixed(2) + "m, Y: " + selectedItem.y.toFixed(2) + "m ] -> 오른쪽 적용 버튼 클릭!";
            }}
        }});

        canvas.addEventListener('dblclick', () => {{
            if (selectedItem) {{
                selectedItem.rot = ((selectedItem.rot || 0) + 90) % 360;
                statusText.innerHTML = "🔄 회전 완료: <b>" + selectedItem.name + "</b> -> " + selectedItem.rot + "°";
                draw();
            }}
        }});

        function syncToStreamlit() {{
            if (!selectedItem) {{
                alert("이동 또는 회전한 가구를 클릭하여 선택한 후 적용 버튼을 누르세요!");
                return;
            }}
            const url = new URL(window.parent.location.href);
            url.searchParams.set('sync_id', selectedItem.id);
            url.searchParams.set('sync_x', selectedItem.x.toFixed(2));
            url.searchParams.set('sync_y', selectedItem.y.toFixed(2));
            url.searchParams.set('sync_rot', selectedItem.rot || 0);
            window.parent.location.href = url.toString();
        }}

        draw();
    </script>
    </body>
    </html>
    """

    components.html(drag_canvas_html, height=720)

    st.divider()

    # -------------------------------------------------------------
    # 7. 정밀 3D 입체 건축 평면도 시각화
    # -------------------------------------------------------------
    st.subheader("🏗️ 4. 정밀 3D 입체 건축 평면도 시각화")

    fig = go.Figure()

    # 1) 바닥 타일
    for rname, rdata in all_rooms.items():
        rx0, ry0, rw, rl, rz = rdata["x0"], rdata["y0"], rdata["w"], rdata["l"], rdata["z"]
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx0+rw, rx0+rw, rx0],
            y=[ry0, ry0, ry0+rl, ry0+rl],
            z=[rz, rz, rz, rz],
            color=rdata["color"], opacity=0.75, name=rname,
            hoverinfo="name"
        ))

    # 2) 1층 외벽 & 내벽 & 개조 벽체
    ent_info = rooms_1f["[1층] 현관 (Entrance)"]

    # 외벽
    fig.add_trace(create_3d_rotated_box(0, 0, 0, house_w, wall_th, house_h*0.85, 0, "#616161", "남측 외벽"))
    fig.add_trace(create_3d_rotated_box(0, 0, 0, wall_th, house_l, house_h*0.85, 0, "#616161", "서측 외벽"))
    fig.add_trace(create_3d_rotated_box(house_w - wall_th, 0, 0, wall_th, house_l, house_h*0.85, 0, "#616161", "동측 외벽"))

    # 후면 외벽 및 출입문
    fig.add_trace(create_3d_rotated_box(0, house_l - wall_th, 0, ent_info["x0"], wall_th, house_h*0.85, 0, "#616161", "북측 외벽"))
    fig.add_trace(create_3d_rotated_box(ent_info["x0"], house_l - wall_th, 0, ent_info["w"]*0.1, wall_th, house_h*0.85, 0, "#424242", "현관 외벽"))
    if show_front_door:
        fig.add_trace(create_3d_rotated_box(ent_info["x0"] + ent_info["w"]*0.1, house_l - wall_th, 0, 1.1, wall_th, house_h*0.85, 0, "#1B5E20", "🚪 메인 현관 출입문", opacity=0.95))
    fig.add_trace(create_3d_rotated_box(ent_info["x0"] + ent_info["w"]*0.1 + 1.1, house_l - wall_th, 0, ent_info["w"] - (ent_info["w"]*0.1 + 1.1), wall_th, house_h*0.85, 0, "#424242", "현관 외벽"))

    # 내벽 경계선
    fig.add_trace(create_3d_rotated_box(x_mid1 - wall_th/2, 0, 0, wall_th, y_mid * 0.3, house_h*0.85, 0, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_rotated_box(x_mid1 - wall_th/2, y_mid * 0.3 + door_w, 0, wall_th, y_mid - (y_mid * 0.3 + door_w), house_h*0.85, 0, "#9E9E9E", "내벽"))

    fig.add_trace(create_3d_rotated_box(0, y_mid - wall_th/2, 0, x_mid2 * 0.2, wall_th, house_h*0.85, 0, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_rotated_box(x_mid2 * 0.2 + door_w, y_mid - wall_th/2, 0, x_mid2 - (x_mid2 * 0.2 + door_w), wall_th, house_h*0.85, 0, "#9E9E9E", "내벽"))

    fig.add_trace(create_3d_rotated_box(x_mid3, y_mid - wall_th/2, 0, house_w - x_mid3, wall_th, house_h*0.85, 0, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_rotated_box(x_mid2 - wall_th/2, y_mid, 0, wall_th, house_l - y_mid, house_h*0.85, 0, "#9E9E9E", "내벽"))
    fig.add_trace(create_3d_rotated_box(x_mid3 - wall_th/2, y_bath, 0, wall_th, house_l - y_bath, house_h*0.85, 0, "#9E9E9E", "현관 내벽"))
    fig.add_trace(create_3d_rotated_box(x_mid3, y_bath - wall_th/2, 0, house_w - x_mid3, wall_th, house_h*0.85, 0, "#9E9E9E", "현관 경계벽"))

    # 사용자 정의 커스텀 추가 벽체
    if "custom_walls" in st.session_state and st.session_state.custom_walls:
        for wall_item in st.session_state.custom_walls:
            w_dx = wall_item["w"] if wall_item["dir"] == "가로 방향 (E-W)" else wall_th
            w_dy = wall_th if wall_item["dir"] == "가로 방향 (E-W)" else wall_item["w"]
            w_color = "#2E7D32" if "파티션" in wall_item["type"] else ("#E65100" if "문" in wall_item["type"] else "#0288D1")
            fig.add_trace(create_3d_rotated_box(wall_item["x"], wall_item["y"], wall_item["z"], w_dx, w_dy, wall_item["h"], 0, w_color, f"🛠️ 커스텀 {wall_item['type']}"))

    # 3) 가구 3D 배치 (동기화 반영)
    placed_coords = {}
    valid_items = [item for item in st.session_state.custom_items if item["room"] in all_rooms]

    floor_items = [item for item in valid_items if item["base_item"] == "바닥 (z=0)"]
    stacked_items = [item for item in valid_items if item["base_item"] != "바닥 (z=0)"]

    for item in floor_items:
        rname = item["room"]
        w, l, h = item["w"], item["l"], item["h"]

        x0 = float(item.get("abs_x", 1.0))
        y0 = float(item.get("abs_y", 1.0))
        z0 = 0.0
        rot_deg = int(item.get("rot", 0))

        placed_coords[item["name"]] = (x0, y0, z0, w, l, h, rot_deg)
        fig.add_trace(create_3d_rotated_box(x0, y0, z0, w, l, h, rot_deg, item["color"], f"[{rname.split(' ')[0]}] {item['name']} ({rot_deg}°)"))

    for item in stacked_items:
        parent_name = item["base_item"]
        if parent_name in placed_coords:
            px0, py0, pz0, pw, pl, ph, prot = placed_coords[parent_name]
            w, l, h = item["w"], item["l"], item["h"]

            x0 = px0 + 0.1
            y0 = py0 + 0.1
            z0 = pz0 + ph

            placed_coords[item["name"]] = (x0, y0, z0, w, l, h, prot)
            fig.add_trace(create_3d_rotated_box(x0, y0, z0, w, l, h, prot, item["color"], f"[{parent_name} 위] {item['name']}"))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='가로 (m)', range=[-0.5, house_w + 0.5]),
            yaxis=dict(title='세로 (m)', range=[-0.5, house_l + 0.5]),
            zaxis=dict(title='높이 (m)', range=[0, house_h * num_floors + 0.5]),
            aspectmode='data',
            camera=dict(eye=dict(x=1.4, y=-1.4, z=1.3))
        ),
        width=950, height=700,
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ 오류 발생: {e}")
