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
st.caption("2D 평면도 내 직접 벽체/가구 드래그 조작 | 마우스 드래그 종료 시 3D 실시간 자동 반영 | R키+마우스 휠 360도 가구 회전")

st.divider()

# -------------------------------------------------------------
# 2. 안전한 형변환 및 헬퍼 함수
# -------------------------------------------------------------
def safe_float(val, default=0.0):
    """단일 값 또는 리스트 형태의 query_params 안전 변환 헬퍼"""
    if isinstance(val, (list, tuple)):
        val = val[0] if len(val) > 0 else default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def safe_int(val, default=0):
    """단일 값 또는 리스트 형태의 query_params 안전 변환 헬퍼"""
    if isinstance(val, (list, tuple)):
        val = val[0] if len(val) > 0 else default
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return default

def create_3d_rotated_box(x0, y0, z0, dx, dy, dz, angle_deg=0, color="#888888", name="구조물", opacity=0.85):
    """Plotly 3D 직육면체 메쉬 생성 (Z축 중심 360도 회전)"""
    x0, y0, z0 = safe_float(x0), safe_float(y0), safe_float(z0)
    dx, dy, dz = safe_float(dx), safe_float(dy), safe_float(dz)
    angle_deg = safe_float(angle_deg)

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
    # -------------------------------------------------------------
    # 3. 건축 전체 치수 및 상단 기본 설정
    # -------------------------------------------------------------
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

    # 세션 상태 벽 위치 초기화
    if "y_mid" not in st.session_state:
        st.session_state.y_mid = house_l * 0.55
    if "x_mid1" not in st.session_state:
        st.session_state.x_mid1 = house_w * 0.5
    if "x_mid2" not in st.session_state:
        st.session_state.x_mid2 = house_w * 0.38
    if "x_mid3" not in st.session_state:
        st.session_state.x_mid3 = house_w * 0.75
    if "y_bath" not in st.session_state:
        st.session_state.y_bath = house_l * 0.80

    y_mid = safe_float(st.session_state.y_mid, house_l * 0.55)
    x_mid1 = safe_float(st.session_state.x_mid1, house_w * 0.5)
    x_mid2 = safe_float(st.session_state.x_mid2, house_w * 0.38)
    x_mid3 = safe_float(st.session_state.x_mid3, house_w * 0.75)
    y_bath = safe_float(st.session_state.y_bath, house_l * 0.80)

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
    # 4. 🤖 AI 스마트 공간 자동 가구 분산 배치 함수
    # -------------------------------------------------------------
    def apply_ai_smart_layout():
        r_liv = rooms_1f["[1층] 거실 (Living Room)"]
        r_mas = rooms_1f["[1층] 안방 (Master Bedroom)"]
        r_bed2 = rooms_1f["[1층] 작은방 (Bedroom 2)"]
        r_kit = rooms_1f["[1층] 주방/식당 (Kitchen)"]
        r_bath = rooms_1f["[1층] 욕실/화장실 (Bathroom)"]
        r_ent = rooms_1f["[1층] 현관 (Entrance)"]

        st.session_state.custom_items = [
            {"name": "4인용 패브릭 소파", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_liv["x0"] + 0.3, "abs_y": r_liv["y0"] + 0.2, "w": min(2.4, r_liv["w"]-0.6), "l": 0.9, "h": 0.85, "color": "#5C6BC0", "rot": 0},
            {"name": "원목 소파 테이블", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_liv["x0"] + 0.8, "abs_y": r_liv["y0"] + 1.4, "w": 1.1, "l": 0.6, "h": 0.4, "color": "#8D6E63", "rot": 0},
            {"name": "대형 거실 TV장", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_liv["x0"] + 0.5, "abs_y": r_liv["y0"] + r_liv["l"] - 0.55, "w": min(2.0, r_liv["w"]-0.8), "l": 0.4, "h": 0.5, "color": "#4E342E", "rot": 0},
            {"name": "75인치 스마트 TV", "room": "[1층] 거실 (Living Room)", "type": "일반 가구", "base_item": "대형 거실 TV장", "abs_x": r_liv["x0"] + 0.7, "abs_y": r_liv["y0"] + r_liv["l"] - 0.5, "w": 1.6, "l": 0.15, "h": 0.9, "color": "#1A237E", "rot": 0},

            {"name": "퀸 사이즈 침대", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_mas["x0"] + r_mas["w"] - 1.8, "abs_y": r_mas["y0"] + 0.3, "w": 1.6, "l": 2.1, "h": 0.55, "color": "#3949AB", "rot": 0},
            {"name": "원목 침대 협탁", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_mas["x0"] + r_mas["w"] - 2.4, "abs_y": r_mas["y0"] + 0.3, "w": 0.5, "l": 0.4, "h": 0.5, "color": "#A1887F", "rot": 0},
            {"name": "안방 대형 붙박이장", "room": "[1층] 안방 (Master Bedroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_mas["x0"] + 0.3, "abs_y": r_mas["y0"] + r_mas["l"] - 0.7, "w": min(2.2, r_mas["w"]-0.6), "l": 0.65, "h": 2.1, "color": "#6D4C41", "rot": 0},

            {"name": "슈퍼싱글 침대", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bed2["x0"] + 0.2, "abs_y": r_bed2["y0"] + 0.3, "w": 1.1, "l": 2.0, "h": 0.5, "color": "#0288D1", "rot": 0},
            {"name": "1인용 집중 스터디 책상", "room": "[1층] 작은방 (Bedroom 2)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bed2["x0"] + r_bed2["w"] - 1.3, "abs_y": r_bed2["y0"] + 0.3, "w": 1.2, "l": 0.7, "h": 0.75, "color": "#26A69A", "rot": 0},

            {"name": "4인용 아일랜드 식탁", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_kit["x0"] + 0.2, "abs_y": r_kit["y0"] + 0.8, "w": min(1.4, r_kit["w"]-0.4), "l": 0.8, "h": 0.75, "color": "#66BB6A", "rot": 0},
            {"name": "양문형 비스포크 냉장고", "room": "[1층] 주방/식당 (Kitchen)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_kit["x0"] + r_kit["w"] - 1.05, "abs_y": r_kit["y0"] + 0.2, "w": 0.95, "l": 0.9, "h": 1.85, "color": "#78909C", "rot": 0},

            {"name": "양변기 & 세면대 세트", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bath["x0"] + 0.15, "abs_y": r_bath["y0"] + 0.15, "w": min(0.9, r_bath["w"]-0.2), "l": 0.6, "h": 0.8, "color": "#00BCD4", "rot": 0},
            {"name": "유리 샤워부스/욕조", "room": "[1층] 욕실/화장실 (Bathroom)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_bath["x0"] + r_bath["w"] - 0.95, "abs_y": r_bath["y0"] + 0.15, "w": min(0.9, r_bath["w"]-0.2), "l": 0.9, "h": 1.9, "color": "#4DD0E1", "rot": 0},

            {"name": "🚪 현관 슬라이딩 중문", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_ent["x0"] + 0.1, "abs_y": r_ent["y0"] + 0.05, "w": min(1.2, r_ent["w"]-0.2), "l": 0.1, "h": 2.1, "color": "#3E2723", "rot": 0},
            {"name": "신발장 및 전신거울", "room": "[1층] 현관 (Entrance)", "type": "일반 가구", "base_item": "바닥 (z=0)", "abs_x": r_ent["x0"] + r_ent["w"] - 0.45, "abs_y": r_ent["y0"] + 0.2, "w": 0.4, "l": min(1.0, r_ent["l"]-0.3), "h": 1.4, "color": "#795548", "rot": 0}
        ]

    # custom_items 우선 생성보장
    if "custom_items" not in st.session_state:
        apply_ai_smart_layout()

    # -------------------------------------------------------------
    # 4.5. URL 쿼리 파라미터 (sync_all, sync_wall, sync_id) 수신 처리
    # (custom_items가 세션에 확정된 후 반영하므로 누락 방지!)
    # -------------------------------------------------------------
    query_params = st.query_params
    
    if "sync_all" in query_params:
        try:
            if "walls" in query_params:
                w_raw = query_params["walls"]
                w_str = w_raw[0] if isinstance(w_raw, list) else w_raw
                walls_data = json.loads(w_str)
                st.session_state.y_mid = safe_float(walls_data.get("y_mid"), 4.4)
                st.session_state.x_mid1 = safe_float(walls_data.get("x_mid1"), 5.0)
                st.session_state.x_mid2 = safe_float(walls_data.get("x_mid2"), 3.8)
                st.session_state.x_mid3 = safe_float(walls_data.get("x_mid3"), 7.5)
                st.session_state.y_bath = safe_float(walls_data.get("y_bath"), 6.4)

            if "items" in query_params:
                i_raw = query_params["items"]
                i_str = i_raw[0] if isinstance(i_raw, list) else i_raw
                items_data = json.loads(i_str)
                for item_state in items_data:
                    s_id = safe_int(item_state.get("id"), -1)
                    if 0 <= s_id < len(st.session_state.custom_items):
                        st.session_state.custom_items[s_id]["abs_x"] = safe_float(item_state.get("x"))
                        st.session_state.custom_items[s_id]["abs_y"] = safe_float(item_state.get("y"))
                        st.session_state.custom_items[s_id]["rot"] = safe_int(item_state.get("rot"))
            
            st.toast("⚡ 2D 평면도 조작 내용이 3D 모델에 실시간 반영되었습니다!", icon="✨")
        except Exception:
            pass

    if "sync_wall" in query_params:
        try:
            st.session_state.y_mid = safe_float(query_params.get("y_mid"), st.session_state.get("y_mid", 4.4))
            st.session_state.x_mid1 = safe_float(query_params.get("x_mid1"), st.session_state.get("x_mid1", 5.0))
            st.session_state.x_mid2 = safe_float(query_params.get("x_mid2"), st.session_state.get("x_mid2", 3.8))
            st.session_state.x_mid3 = safe_float(query_params.get("x_mid3"), st.session_state.get("x_mid3", 7.5))
            st.session_state.y_bath = safe_float(query_params.get("y_bath"), st.session_state.get("y_bath", 6.4))
        except Exception:
            pass

    if "sync_id" in query_params:
        try:
            s_id = safe_int(query_params.get("sync_id"), -1)
            s_x = safe_float(query_params.get("sync_x"), 0.0)
            s_y = safe_float(query_params.get("sync_y"), 0.0)
            s_rot = safe_int(query_params.get("sync_rot"), 0)
            
            if 0 <= s_id < len(st.session_state.custom_items):
                st.session_state.custom_items[s_id]["abs_x"] = s_x
                st.session_state.custom_items[s_id]["abs_y"] = s_y
                st.session_state.custom_items[s_id]["rot"] = s_rot
        except Exception:
            pass

    # 파라미터로 최신화된 벽 위치 재동기화
    y_mid = safe_float(st.session_state.y_mid, house_l * 0.55)
    x_mid1 = safe_float(st.session_state.x_mid1, house_w * 0.5)
    x_mid2 = safe_float(st.session_state.x_mid2, house_w * 0.38)
    x_mid3 = safe_float(st.session_state.x_mid3, house_w * 0.75)
    y_bath = safe_float(st.session_state.y_bath, house_l * 0.80)

    rooms_1f = {
        "[1층] 거실 (Living Room)": {"x0": 0, "y0": 0, "w": x_mid1, "l": y_mid, "color": "#FAFAFA", "z": 0},
        "[1층] 안방 (Master Bedroom)": {"x0": x_mid1, "y0": 0, "w": house_w - x_mid1, "l": y_mid, "color": "#F3E5F5", "z": 0},
        "[1층] 작은방 (Bedroom 2)": {"x0": 0, "y0": y_mid, "w": x_mid2, "l": house_l - y_mid, "color": "#E1F5FE", "z": 0},
        "[1층] 주방/식당 (Kitchen)": {"x0": x_mid2, "y0": y_mid, "w": max(0.5, x_mid3 - x_mid2), "l": house_l - y_mid, "color": "#FFF3E0", "z": 0},
        "[1층] 욕실/화장실 (Bathroom)": {"x0": x_mid3, "y0": y_mid, "w": house_w - x_mid3, "l": max(0.5, y_bath - y_mid), "color": "#E0F7FA", "z": 0},
        "[1층] 현관 (Entrance)": {"x0": x_mid3, "y0": y_bath, "w": house_w - x_mid3, "l": house_l - y_bath, "color": "#E8EAF6", "z": 0}
    }
    all_rooms = {**rooms_1f, **rooms_2f}

    # -------------------------------------------------------------
    # 5. 🎮 [배치도 캔버스 통합 메인 제어 화면]
    # -------------------------------------------------------------
    st.subheader("🎮 2D 스마트 평면도 통합 편집기 (드래그 시 3D 모델에 실시간 자동 반영)")

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([3, 2.5, 2.5])
    with ctrl_col1:
        if st.button("✨ AI 기반 인간공학 자동 공간 최적화 재배치", use_container_width=True):
            apply_ai_smart_layout()
            st.success("🤖 각 방별 동선과 치수에 맞춰 가구를 자동 최적화 배치했습니다!")
            st.rerun()
    with ctrl_col2:
        show_room_names = st.checkbox("🏷️ 방 이름 표시", value=True)
    with ctrl_col3:
        show_item_names = st.checkbox("🏷️ 가구 이름 표시", value=True)

    canvas_items_json = []
    for idx, item in enumerate(st.session_state.custom_items):
        canvas_items_json.append({
            "id": idx, "name": item["name"], "room": item["room"],
            "x": safe_float(item.get("abs_x", 1.0)), "y": safe_float(item.get("abs_y", 1.0)),
            "w": safe_float(item["w"]), "l": safe_float(item["l"]), "color": item["color"],
            "rot": safe_int(item.get("rot", 0)), "is_base": (item["base_item"] == "바닥 (z=0)")
        })

    wall_data_json = {
        "y_mid": safe_float(y_mid),
        "x_mid1": safe_float(x_mid1),
        "x_mid2": safe_float(x_mid2),
        "x_mid3": safe_float(x_mid3),
        "y_bath": safe_float(y_bath)
    }

    drag_canvas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 5px; background-color: #f8f9fa; }}
        #canvas-container {{ position: relative; width: 100%; text-align: center; }}
        canvas {{ border: 3px solid #343a40; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
        .status-bar {{ margin-top: 8px; padding: 10px; background: #212529; color: #f8f9fa; border-radius: 6px; font-weight: bold; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }}
        .sync-btn {{ background-color: #0d6efd; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-left: 5px; }}
        .sync-btn:hover {{ background-color: #0b5ed7; }}
        .guide-banner {{ background: #e7f5ff; border: 1px solid #a5d8ff; padding: 8px; border-radius: 6px; font-size: 13px; color: #1864ab; font-weight: bold; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }}
        .badge {{ background-color: #d0ebff; color: #1864ab; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-left: 4px; }}
    </style>
    </head>
    <body>
    <div id="canvas-container">
        <div class="guide-banner">
            <div>
                💡 <b>조작법:</b> <b>벽체선</b> 마우스 드래그로 방 크기 개조 | <b>가구</b> 클릭 후 드래그 이동 | <b>'R'키+마우스 휠</b> 360도 미세 회전
            </div>
            <div>
                <span class="badge" style="background-color:#d4edda; color:#155724; border: 1px solid #c3e6cb;">⚡ 마우스 놓을 때 3D 실시간 자동 반영</span>
            </div>
        </div>
        <canvas id="floorCanvas" width="900" height="650"></canvas>
        <div class="status-bar">
            <span id="statusText">🎮 평면도 상의 내벽/가구를 마우스로 이동하면 3D 모델에 바로 실시간 반영됩니다!</span>
            <div>
                <button class="sync-btn" style="background-color:#198754;" onclick="syncAllToStreamlit()">⚡ 3D 모델에 지금 실시간 반영</button>
            </div>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('floorCanvas');
        const ctx = canvas.getContext('2d');
        const statusText = document.getElementById('statusText');

        const houseW = {house_w};
        const houseL = {house_l};

        const showRoomNames = {str(show_room_names).lower()};
        const showItemNames = {str(show_item_names).lower()};

        const scale = 75; // 1m = 75px
        const originX = 60;
        const originY = 50;

        let walls = {json.dumps(wall_data_json)};
        let items = {json.dumps(canvas_items_json)};

        let selectedItem = null;
        let activeWall = null;
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;
        let isRPressed = false;
        let rotTimer = null;

        function getRooms() {{
            return [
                {{ name: "거실", x: 0, y: 0, w: walls.x_mid1, l: walls.y_mid, color: "#FAFAFA" }},
                {{ name: "안방", x: walls.x_mid1, y: 0, w: houseW - walls.x_mid1, l: walls.y_mid, color: "#F3E5F5" }},
                {{ name: "작은방", x: 0, y: walls.y_mid, w: walls.x_mid2, l: houseL - walls.y_mid, color: "#E1F5FE" }},
                {{ name: "주방/식당", x: walls.x_mid2, y: walls.y_mid, w: Math.max(0.1, walls.x_mid3 - walls.x_mid2), l: houseL - walls.y_mid, color: "#FFF3E0" }},
                {{ name: "욕실/화장실", x: walls.x_mid3, y: walls.y_mid, w: houseW - walls.x_mid3, l: Math.max(0.1, walls.y_bath - walls.y_mid), color: "#E0F7FA" }},
                {{ name: "현관", x: walls.x_mid3, y: walls.y_bath, w: houseW - walls.x_mid3, l: houseL - walls.y_bath, color: "#E8EAF6" }}
            ];
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const roomsList = getRooms();

            roomsList.forEach(r => {{
                let rx = originX + r.x * scale;
                let ry = originY + r.y * scale;
                let rw = r.w * scale;
                let rl = r.l * scale;

                ctx.fillStyle = r.color;
                ctx.fillRect(rx, ry, rw, rl);
                ctx.strokeStyle = "#adb5bd";
                ctx.lineWidth = 1;
                ctx.strokeRect(rx, ry, rw, rl);

                if (showRoomNames) {{
                    ctx.fillStyle = "#495057";
                    ctx.font = "bold 13px sans-serif";
                    ctx.fillText(r.name, rx + 8, ry + 20);
                }}
            }});

            ctx.strokeStyle = "#212529";
            ctx.lineWidth = 6;
            ctx.strokeRect(originX, originY, houseW * scale, houseL * scale);

            drawWallLine("y_mid", originX, originY + walls.y_mid * scale, originX + houseW * scale, originY + walls.y_mid * scale, "horizontal");
            drawWallLine("x_mid1", originX + walls.x_mid1 * scale, originY, originX + walls.x_mid1 * scale, originY + walls.y_mid * scale, "vertical");
            drawWallLine("x_mid2", originX + walls.x_mid2 * scale, originY + walls.y_mid * scale, originX + walls.x_mid2 * scale, originY + houseL * scale, "vertical");
            drawWallLine("x_mid3", originX + walls.x_mid3 * scale, originY + walls.y_mid * scale, originX + walls.x_mid3 * scale, originY + houseL * scale, "vertical");
            drawWallLine("y_bath", originX + walls.x_mid3 * scale, originY + walls.y_bath * scale, originX + houseW * scale, originY + walls.y_bath * scale, "horizontal");

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
                    ctx.fillRect(-iw/2 - 5, -il/2 - 5, iw + 10, il + 10);
                    ctx.strokeStyle = "#d39e00";
                    ctx.lineWidth = 3;
                    ctx.strokeRect(-iw/2 - 5, -il/2 - 5, iw + 10, il + 10);
                }}

                ctx.fillStyle = item.color;
                ctx.fillRect(-iw/2, -il/2, iw, il);
                ctx.strokeStyle = "#000000";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(-iw/2, -il/2, iw, il);

                if (showItemNames) {{
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "bold 11px sans-serif";
                    ctx.shadowColor = "black";
                    ctx.shadowBlur = 3;
                    ctx.fillText(item.name.substring(0, 8), -iw/2 + 3, 4);
                    ctx.shadowBlur = 0;
                }}

                ctx.restore();
            }});
        }}

        function drawWallLine(wallKey, x1, y1, x2, y2, orientation) {{
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.lineWidth = (activeWall === wallKey) ? 7 : 5;
            ctx.strokeStyle = (activeWall === wallKey) ? "#e63946" : "#495057";
            ctx.stroke();

            let midX = (x1 + x2) / 2;
            let midY = (y1 + y2) / 2;
            ctx.fillStyle = (activeWall === wallKey) ? "#e63946" : "#212529";
            ctx.beginPath();
            ctx.arc(midX, midY, 6, 0, Math.PI * 2);
            ctx.fill();
        }}

        function checkWallHover(mx, my) {{
            const tolerance = 8;
            
            let y_mid_px = originY + walls.y_mid * scale;
            if (Math.abs(my - y_mid_px) <= tolerance && mx >= originX && mx <= originX + houseW * scale) return 'y_mid';

            let x_mid1_px = originX + walls.x_mid1 * scale;
            if (Math.abs(mx - x_mid1_px) <= tolerance && my >= originY && my <= originY + walls.y_mid * scale) return 'x_mid1';

            let x_mid2_px = originX + walls.x_mid2 * scale;
            if (Math.abs(mx - x_mid2_px) <= tolerance && my >= originY + walls.y_mid * scale && my <= originY + houseL * scale) return 'x_mid2';

            let x_mid3_px = originX + walls.x_mid3 * scale;
            if (Math.abs(mx - x_mid3_px) <= tolerance && my >= originY + walls.y_mid * scale && my <= originY + houseL * scale) return 'x_mid3';

            let y_bath_px = originY + walls.y_bath * scale;
            if (Math.abs(my - y_bath_px) <= tolerance && mx >= originX + walls.x_mid3 * scale && mx <= originX + houseW * scale) return 'y_bath';

            return null;
        }}

        canvas.addEventListener('mousedown', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            let hoveredWall = checkWallHover(mx, my);
            if (hoveredWall) {{
                activeWall = hoveredWall;
                isDragging = true;
                selectedItem = null;
                statusText.innerHTML = "🧱 내벽선 조절 중: <b>" + activeWall + "</b>";
                draw();
                return;
            }}

            for (let i = items.length - 1; i >= 0; i--) {{
                let item = items[i];
                if (!item.is_base) continue;
                
                let ix = originX + item.x * scale;
                let iy = originY + item.y * scale;
                let iw = item.w * scale;
                let il = item.l * scale;

                if (mx >= ix && mx <= ix + iw && my >= iy && my <= iy + il) {{
                    selectedItem = item;
                    activeWall = null;
                    isDragging = true;
                    dragOffsetX = mx - ix;
                    dragOffsetY = my - iy;
                    statusText.innerHTML = "🎯 선택된 가구: <b>" + item.name + "</b> (각도: " + (item.rot||0) + "°)";
                    draw();
                    return;
                }}
            }}

            selectedItem = null;
            activeWall = null;
            statusText.innerHTML = "🎮 평면도 상의 내벽/가구를 마우스 커서로 잡고 이동하세요!";
            draw();
        }});

        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            if (!isDragging) {{
                let hoveredWall = checkWallHover(mx, my);
                if (hoveredWall) {{
                    canvas.style.cursor = hoveredWall.startsWith('y') ? 'ns-resize' : 'ew-resize';
                }} else {{
                    canvas.style.cursor = 'default';
                }}
            }}

            if (!isDragging) return;

            if (activeWall) {{
                let mValX = (mx - originX) / scale;
                let mValY = (my - originY) / scale;

                if (activeWall === 'y_mid') {{
                    walls.y_mid = Math.max(1.5, Math.min(houseL - 1.5, mValY));
                }} else if (activeWall === 'x_mid1') {{
                    walls.x_mid1 = Math.max(1.0, Math.min(houseW - 1.0, mValX));
                }} else if (activeWall === 'x_mid2') {{
                    walls.x_mid2 = Math.max(0.8, Math.min(walls.x_mid3 - 0.5, mValX));
                }} else if (activeWall === 'x_mid3') {{
                    walls.x_mid3 = Math.max(walls.x_mid2 + 0.5, Math.min(houseW - 0.8, mValX));
                }} else if (activeWall === 'y_bath') {{
                    walls.y_bath = Math.max(walls.y_mid + 0.5, Math.min(houseL - 0.5, mValY));
                }}

                statusText.innerHTML = "🧱 벽 조절 중: <b>" + activeWall + "</b> [ 위치: " + 
                    (activeWall.startsWith('y') ? walls[activeWall].toFixed(2) + "m (Y)" : walls[activeWall].toFixed(2) + "m (X)") + " ]";
                draw();
                return;
            }}

            if (selectedItem) {{
                let newX = (mx - dragOffsetX - originX) / scale;
                let newY = (my - dragOffsetY - originY) / scale;

                selectedItem.x = Math.max(0, Math.min(houseW - selectedItem.w, newX));
                selectedItem.y = Math.max(0, Math.min(houseL - selectedItem.l, newY));

                statusText.innerHTML = "🚚 가구 이동 중: <b>" + selectedItem.name + "</b> [ X: " + selectedItem.x.toFixed(2) + "m, Y: " + selectedItem.y.toFixed(2) + "m ]";
                draw();
            }}
        }});

        window.addEventListener('mouseup', () => {{
            if (isDragging) {{
                isDragging = false;
                statusText.innerHTML = "⚡ 3D 모델에 변경사항 실시간 자동 반영 중...";
                syncAllToStreamlit();
            }}
        }});

        window.addEventListener('keydown', (e) => {{
            if (e.key === 'r' || e.key === 'R') {{
                isRPressed = true;
            }}
        }});

        window.addEventListener('keyup', (e) => {{
            if (e.key === 'r' || e.key === 'R') {{
                isRPressed = false;
            }}
        }});

        canvas.addEventListener('wheel', (e) => {{
            if (selectedItem && isRPressed) {{
                e.preventDefault();
                let rotStep = e.deltaY < 0 ? 5 : -5;
                selectedItem.rot = ((selectedItem.rot || 0) + rotStep + 360) % 360;
                statusText.innerHTML = "🔄 가구 회전: <b>" + selectedItem.name + "</b> -> " + selectedItem.rot + "°";
                draw();

                clearTimeout(rotTimer);
                rotTimer = setTimeout(() => {{
                    syncAllToStreamlit();
                }}, 300);
            }}
        }}, {{ passive: false }});

        function syncAllToStreamlit() {{
            const url = new URL(window.parent.location.href);
            url.searchParams.set('sync_all', '1');
            
            const wData = {{
                y_mid: parseFloat(walls.y_mid.toFixed(2)),
                x_mid1: parseFloat(walls.x_mid1.toFixed(2)),
                x_mid2: parseFloat(walls.x_mid2.toFixed(2)),
                x_mid3: parseFloat(walls.x_mid3.toFixed(2)),
                y_bath: parseFloat(walls.y_bath.toFixed(2))
            }};
            url.searchParams.set('walls', JSON.stringify(wData));

            const itemStates = items.map(it => ({{
                id: it.id,
                x: parseFloat(it.x.toFixed(2)),
                y: parseFloat(it.y.toFixed(2)),
                rot: it.rot || 0
            }}));
            url.searchParams.set('items', JSON.stringify(itemStates));

            window.parent.location.href = url.toString();
        }}

        draw();
    </script>
    </body>
    </html>
    """

    components.html(drag_canvas_html, height=730)

    st.divider()

    # -------------------------------------------------------------
    # 6. 정밀 3D 입체 건축 평면도 시각화
    # -------------------------------------------------------------
    st.subheader("🏗️ 3D 입체 건축 평면도 시각화 (실시간 반영)")

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

    # 2) 1층 외벽 & 내벽
    ent_info = rooms_1f["[1층] 현관 (Entrance)"]

    fig.add_trace(create_3d_rotated_box(0, 0, 0, house_w, wall_th, house_h*0.85, 0, "#616161", "남측 외벽"))
    fig.add_trace(create_3d_rotated_box(0, 0, 0, wall_th, house_l, house_h*0.85, 0, "#616161", "서측 외벽"))
    fig.add_trace(create_3d_rotated_box(house_w - wall_th, 0, 0, wall_th, house_l, house_h*0.85, 0, "#616161", "동측 외벽"))

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

    # 3) 가구 3D 배치 (동기화 반영)
    placed_coords = {}
    valid_items = [item for item in st.session_state.custom_items if item["room"] in all_rooms]

    floor_items = [item for item in valid_items if item["base_item"] == "바닥 (z=0)"]
    stacked_items = [item for item in valid_items if item["base_item"] != "바닥 (z=0)"]

    for item in floor_items:
        rname = item["room"]
        w = safe_float(item["w"])
        l = safe_float(item["l"])
        h = safe_float(item["h"])

        x0 = safe_float(item.get("abs_x", 1.0))
        y0 = safe_float(item.get("abs_y", 1.0))
        z0 = 0.0
        rot_deg = safe_int(item.get("rot", 0))

        placed_coords[item["name"]] = (x0, y0, z0, w, l, h, rot_deg)
        fig.add_trace(create_3d_rotated_box(x0, y0, z0, w, l, h, rot_deg, item["color"], f"[{rname.split(' ')[0]}] {item['name']} ({rot_deg}°)"))

    for item in stacked_items:
        parent_name = item["base_item"]
        if parent_name in placed_coords:
            px0, py0, pz0, pw, pl, ph, prot = placed_coords[parent_name]
            w = safe_float(item["w"])
            l = safe_float(item["l"])
            h = safe_float(item["h"])

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
