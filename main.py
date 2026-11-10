import os
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(page_title="AI 건축 평면도 & 3D 스마트 인테리어", layout="wide")

# 1. 2D 커스텀 컴포넌트 로드
parent_dir = os.path.dirname(os.path.abspath(__file__))
component_dir = os.path.join(parent_dir, "canvas_component")
interactive_canvas = components.declare_component("interactive_canvas", path=component_dir)

# 2. 기본 가구 및 내벽 데이터
DEFAULT_WALLS = {
    "y_mid": 4.4,
    "x_mid1": 5.0,
    "x_mid2": 3.8,
    "x_mid3": 7.5,
    "y_bath": 6.4
}

DEFAULT_ITEMS = [
    {"id": "carpet_living", "name": "거실 카페트", "type": "carpet", "x": 0.5, "y": 0.5, "w": 3.0, "l": 2.2, "h": 0.02, "z_base": 0.02, "rot": 0.0, "color": "#CBD5E1"},
    {"id": "sofa", "name": "거실 소파", "type": "furniture", "x": 0.8, "y": 0.8, "w": 2.4, "l": 1.2, "h": 0.9, "z_base": 0.05, "rot": 0.0, "color": "#EF4444"},
    {"id": "tv", "name": "TV장", "type": "furniture", "x": 0.8, "y": 2.8, "w": 1.8, "l": 0.6, "h": 0.6, "z_base": 0.05, "rot": 0.0, "color": "#3B82F6"},
    {"id": "bed", "name": "안방 침대", "type": "furniture", "x": 5.5, "y": 0.8, "w": 2.0, "l": 2.0, "h": 1.1, "z_base": 0.05, "rot": 0.0, "color": "#A855F7"},
    {"id": "table", "name": "주방 식탁", "type": "furniture", "x": 4.2, "y": 4.8, "w": 1.8, "l": 1.1, "h": 0.8, "z_base": 0.05, "rot": 0.0, "color": "#F59E0B"},
    {"id": "fridge", "name": "냉장고", "type": "furniture", "x": 7.8, "y": 4.6, "w": 1.0, "l": 1.0, "h": 1.8, "z_base": 0.05, "rot": 0.0, "color": "#10B981"},
    {"id": "desk", "name": "작은방 책상", "type": "furniture", "x": 0.8, "y": 4.8, "w": 1.4, "l": 0.9, "h": 0.75, "z_base": 0.05, "rot": 0.0, "color": "#14B8A6"},
    {"id": "laptop", "name": "노트북(책상위)", "type": "on_top", "x": 1.2, "y": 5.0, "w": 0.5, "l": 0.4, "h": 0.2, "z_base": 0.80, "rot": 0.0, "color": "#334155"},
    {"id": "frame", "name": "벽면 액자", "type": "wall_art", "x": 2.0, "y": 0.05, "w": 1.2, "l": 0.15, "h": 0.8, "z_base": 1.40, "rot": 0.0, "color": "#F59E0B"}
]

# 3. 세션 초기화
if "v3_walls" not in st.session_state:
    st.session_state["v3_walls"] = dict(DEFAULT_WALLS)

if "v3_items" not in st.session_state:
    st.session_state["v3_items"] = list(DEFAULT_ITEMS)

if "show_labels" not in st.session_state:
    st.session_state["show_labels"] = True

# 4. 앱 헤더 및 설정 컨트롤
st.title("🏡 AI 건축 평면도 & 3D 스마트 인테리어")

top_col1, top_col2, top_col3, top_col4 = st.columns([2, 2, 2, 2])
with top_col1:
    house_w = float(st.number_input("가로 폭 (m):", min_value=5.0, max_value=20.0, value=10.0, step=0.5))
with top_col2:
    house_l = float(st.number_input("세로 길이 (m):", min_value=5.0, max_value=20.0, value=8.0, step=0.5))
with top_col3:
    wall_h = float(st.slider("3D 벽 높이 (m):", min_value=2.0, max_value=4.0, value=2.5, step=0.1))
with top_col4:
    st.write("")
    st.write("")
    st.session_state["show_labels"] = st.checkbox("🏷️ 가구/소품 이름 표시", value=st.session_state["show_labels"])

st.write(f"🏠 **전체 주택 연면적:** `{house_w * house_l:.2f} m²` (약 `{house_w * house_l / 3.3058:.1f}평`) | **벽 높이:** `{wall_h}m`")

# 5. 가구 추가 & 삭제 관리 아코디언 메뉴 (사용자 요구 기능 완벽 복구!)
with st.expander("➕ / 🗑️ **가구 & 소품 신규 추가 / 삭제 관리 메뉴**", expanded=True):
    tab1, tab2 = st.tabs(["➕ 가구/소품 추가하기", "🗑️ 가구/소품 삭제하기"])
    
    with tab1:
        c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
        with c1:
            new_name = st.text_input("가구/소품 이름", value="주방 전자레인지")
            new_type_label = st.selectbox("배치 방식 (위치 유형)", ["가구 위 소품 (식탁/책상 위)", "일반 가구 (바닥 배치)", "바닥 카페트 (투명 깔개)", "벽면 액자 (벽 부착)"])
        
        type_map = {
            "가구 위 소품 (식탁/책상 위)": ("on_top", 0.85, 0.25),
            "일반 가구 (바닥 배치)": ("furniture", 0.05, 0.80),
            "바닥 카페트 (투명 깔개)": ("carpet", 0.02, 0.02),
            "벽면 액자 (벽 부착)": ("wall_art", 1.40, 0.80)
        }
        item_type, default_z, default_h = type_map[new_type_label]
        
        with c2:
            new_w = float(st.number_input("가로 폭 (m)", min_value=0.1, max_value=5.0, value=0.6, step=0.1))
            new_l = float(st.number_input("세로 길이 (m)", min_value=0.1, max_value=5.0, value=0.5, step=0.1))
        with c3:
            new_h = float(st.number_input("높이 (m)", min_value=0.01, max_value=3.0, value=default_h, step=0.05))
            new_color = st.color_picker("가구 색상", value="#F59E0B")
        with c4:
            new_x = float(st.number_input("배치 X 위치 (m)", min_value=0.0, max_value=house_w, value=4.5, step=0.5))
            new_y = float(st.number_input("배치 Y 위치 (m)", min_value=0.0, max_value=house_l, value=5.0, step=0.5))
            
        if st.button("➕ 신규 가구/소품 평면도에 추가하기", use_container_width=True):
            new_id = f"item_{len(st.session_state['v3_items']) + 1}_{int(new_x*10)}"
            st.session_state["v3_items"].append({
                "id": new_id,
                "name": new_name,
                "type": item_type,
                "x": new_x,
                "y": new_y,
                "w": new_w,
                "l": new_l,
                "h": new_h,
                "z_base": default_z,
                "rot": 0.0,
                "color": new_color
            })
            st.success(f"'{new_name}' 항목이 성공적으로 추가되었습니다!")
            st.rerun()

    with tab2:
        item_names = [f"{it['name']} (ID: {it['id']})" for it in st.session_state["v3_items"]]
        if item_names:
            del_target = st.selectbox("삭제할 가구 선택", item_names)
            if st.button("🗑️ 선택한 가구 삭제하기", type="primary", use_container_width=True):
                target_idx = item_names.index(del_target)
                deleted_item = st.session_state["v3_items"].pop(target_idx)
                st.warning(f"'{deleted_item['name']}' 항목이 삭제되었습니다.")
                st.rerun()

st.markdown("---")
st.subheader("🎮 2D 평면도 마우스 조작 편집기 (드래그 시 3D 모델에 실시간 반영)")

# 안전 데이터 정제
clean_walls = {str(k): float(v) for k, v in st.session_state["v3_walls"].items()}
clean_items = []
for it in st.session_state["v3_items"]:
    clean_items.append({
        "id": str(it["id"]),
        "name": str(it["name"]),
        "type": str(it.get("type", "furniture")),
        "x": float(it["x"]),
        "y": float(it["y"]),
        "w": float(it["w"]),
        "l": float(it["l"]),
        "h": float(it.get("h", 0.8)),
        "z_base": float(it.get("z_base", 0.05)),
        "rot": float(it.get("rot", 0.0)),
        "color": str(it["color"])
    })

# 2D 평면도 커스텀 컴포넌트 호출
canvas_data = interactive_canvas(
    house_w=house_w,
    house_l=house_l,
    walls=clean_walls,
    items=clean_items,
    show_labels=st.session_state["show_labels"],
    key="interactive_floorplan"
)

if canvas_data and isinstance(canvas_data, dict):
    if "walls" in canvas_data and isinstance(canvas_data["walls"], dict):
        for wk, wv in canvas_data["walls"].items():
            st.session_state["v3_walls"][wk] = float(wv)
            
    if "items" in canvas_data and isinstance(canvas_data["items"], list):
        for updated_it in canvas_data["items"]:
            for original_it in st.session_state["v3_items"]:
                if str(original_it["id"]) == str(updated_it.get("id")):
                    original_it["x"] = float(updated_it.get("x", original_it["x"]))
                    original_it["y"] = float(updated_it.get("y", original_it["y"]))
                    original_it["rot"] = float(updated_it.get("rot", original_it.get("rot", 0.0)))

# --------------------------------------------------------------------------
# 6. 3D 입체 모델 시각화 (Plotly) - 2D와 1:1 완벽 좌표축 정렬
# --------------------------------------------------------------------------
st.markdown("---")
st.subheader("🏗️ 3D 입체 건축 평면도 시각화 (실시간 반영)")

fig = go.Figure()

def create_box_3d(x, y, z, w, l, h, color, name, opacity=0.95):
    x_coords = [x, x + w, x + w, x, x, x + w, x + w, x]
    y_coords = [y, y, y + l, y + l, y, y, y + l, y + l]
    z_coords = [z, z, z, z, z + h, z + h, z + h, z + h]
    
    i = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]
    j = [1, 2, 6, 7, 5, 4, 2, 6, 3, 7, 6, 5]
    k = [2, 3, 5, 6, 1, 5, 6, 7, 7, 4, 2, 6]
    
    return go.Mesh3d(
        x=x_coords, y=y_coords, z=z_coords,
        i=i, j=j, k=k,
        color=color, opacity=opacity, name=name, showscale=False,
        flatshading=True,
        lighting=dict(ambient=0.75, diffuse=0.8, specular=0.2)
    )

def create_wall_3d(x1, y1, x2, y2, height, thickness=0.15, color="#4A4A4A"):
    if x1 == x2:
        return create_box_3d(x1 - thickness/2, min(y1, y2), 0, thickness, abs(y2 - y1), height, color, "벽체")
    else:
        return create_box_3d(min(x1, x2), y1 - thickness/2, 0, abs(x2 - x1), thickness, height, color, "벽체")

# 바닥
fig.add_trace(create_box_3d(0, 0, 0, house_w, house_l, 0.05, "#E2E8F0", "바닥"))

# 3D 외벽
fig.add_trace(create_wall_3d(0, 0, house_w, 0, wall_h))
fig.add_trace(create_wall_3d(0, 0, 0, house_l, wall_h))
fig.add_trace(create_wall_3d(house_w, 0, house_w, house_l, wall_h))
fig.add_trace(create_wall_3d(0, house_l, house_w, house_l, wall_h))

# 3D 내벽
w = st.session_state["v3_walls"]
fig.add_trace(create_wall_3d(0, w["y_mid"], house_w, w["y_mid"], wall_h))
fig.add_trace(create_wall_3d(w["x_mid1"], 0, w["x_mid1"], w["y_mid"], wall_h))
fig.add_trace(create_wall_3d(w["x_mid2"], w["y_mid"], w["x_mid2"], house_l, wall_h))
fig.add_trace(create_wall_3d(w["x_mid3"], w["y_mid"], w["x_mid3"], house_l, wall_h))
fig.add_trace(create_wall_3d(w["x_mid3"], w["y_bath"], house_w, w["y_bath"], wall_h))

# 3D 다층 가구/소품/카페트/액자 배치
for item in st.session_state["v3_items"]:
    item_type = item.get("type", "furniture")
    z_pos = float(item.get("z_base", 0.05))
    h_val = float(item.get("h", 0.8))
    opacity_val = 0.7 if item_type == "carpet" else 0.95
    
    fig.add_trace(create_box_3d(
        x=float(item["x"]),
        y=float(item["y"]),
        z=z_pos,
        w=float(item["w"]),
        l=float(item["l"]),
        h=h_val,
        color=str(item["color"]),
        name=str(item["name"]),
        opacity=opacity_val
    ))

    # 이름 표시 동기화
    if st.session_state["show_labels"]:
        fig.add_trace(go.Scatter3d(
            x=[float(item["x"]) + float(item["w"])/2],
            y=[float(item["y"]) + float(item["l"])/2],
            z=[z_pos + h_val + 0.15],
            mode="text",
            text=[str(item["name"])],
            textposition="top center",
            showlegend=False
        ))

# 2D 평면도와 상하 방향을 1:1 완벽 정렬하기 위해 range=[house_l, 0] 설정
fig.update_layout(
    scene=dict(
        xaxis=dict(range=[0, house_w], title="가로 (m)", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1"),
        yaxis=dict(range=[house_l, 0], title="세로 (m)", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1"),
        zaxis=dict(range=[0, wall_h + 1], title="높이 (m)", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1"),
        aspectmode="data",
        camera=dict(
            eye=dict(x=1.2, y=-1.4, z=1.5),
            center=dict(x=0, y=0, z=-0.2)
        )
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    height=650
)

st.plotly_chart(fig, use_container_width=True)
