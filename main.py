import os
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(page_title="AI 건축 평면도 & 3D 스마트 인테리어", layout="wide")

# 1. 2D 커스텀 컴포넌트 로드
parent_dir = os.path.dirname(os.path.abspath(__file__))
component_dir = os.path.join(parent_dir, "canvas_component")
interactive_canvas = components.declare_component("interactive_canvas", path=component_dir)

# 2. 기본 데이터 정의
DEFAULT_WALLS = {
    "y_mid": 4.4,
    "x_mid1": 5.0,
    "x_mid2": 3.8,
    "x_mid3": 7.5,
    "y_bath": 6.4
}

DEFAULT_ITEMS = [
    {"id": "sofa", "name": "거실 소파", "x": 0.8, "y": 0.8, "w": 2.4, "l": 1.2, "h": 0.9, "rot": 0.0, "color": "#E74C3C"},
    {"id": "tv", "name": "TV장", "x": 0.8, "y": 2.8, "w": 1.8, "l": 0.6, "h": 0.6, "rot": 0.0, "color": "#3498DB"},
    {"id": "bed", "name": "안방 침대", "x": 5.5, "y": 0.8, "w": 2.0, "l": 2.0, "h": 1.1, "rot": 0.0, "color": "#9B59B6"},
    {"id": "table", "name": "주방 식탁", "x": 4.2, "y": 4.8, "w": 1.8, "l": 1.1, "h": 0.8, "rot": 0.0, "color": "#F39C12"},
    {"id": "fridge", "name": "냉장고", "x": 7.8, "y": 4.6, "w": 1.0, "l": 1.0, "h": 1.8, "rot": 0.0, "color": "#2ECC71"},
    {"id": "desk", "name": "작은방 책상", "x": 0.8, "y": 4.8, "w": 1.4, "l": 0.9, "h": 0.75, "rot": 0.0, "color": "#1ABC9C"}
]

# 3. 새로운 세션 키(floorplan_items, floorplan_walls)를 사용하여 캐시 오류 우회
if "floorplan_walls" not in st.session_state or not isinstance(st.session_state["floorplan_walls"], dict):
    st.session_state["floorplan_walls"] = dict(DEFAULT_WALLS)

if "floorplan_items" not in st.session_state or not isinstance(st.session_state["floorplan_items"], list):
    st.session_state["floorplan_items"] = list(DEFAULT_ITEMS)

# 안전한 세션 데이터 추출 함수
def get_safe_items():
    raw = st.session_state.get("floorplan_items")
    if not isinstance(raw, list):
        st.session_state["floorplan_items"] = list(DEFAULT_ITEMS)
        return DEFAULT_ITEMS
    return raw

def get_safe_walls():
    raw = st.session_state.get("floorplan_walls")
    if not isinstance(raw, dict):
        st.session_state["floorplan_walls"] = dict(DEFAULT_WALLS)
        return DEFAULT_WALLS
    return raw

# 4. 상단 컨트롤 UI
st.title("🏡 AI 건축 평면도 & 3D 스마트 인테리어")

col1, col2, col3 = st.columns(3)
with col1:
    house_w_val = st.number_input("가로 폭 (m):", min_value=5.0, max_value=20.0, value=10.0, step=0.5)
with col2:
    house_l_val = st.number_input("세로 길이 (m):", min_value=5.0, max_value=20.0, value=8.0, step=0.5)
with col3:
    wall_h_val = st.slider("3D 벽 높이 (m):", min_value=2.0, max_value=4.0, value=2.5, step=0.1)

house_w = float(house_w_val)
house_l = float(house_l_val)
wall_h = float(wall_h_val)

st.write(f"🏠 **전체 주택 연면적:** `{house_w * house_l:.2f} m²` (약 `{house_w * house_l / 3.3058:.1f}평`) | **벽 높이:** `{wall_h}m`")

st.markdown("---")
st.subheader("🎮 2D 평면도 마우스 조작 편집기 (드래그 시 3D 모델에 실시간 반영)")

# 안전한 데이터 정제
current_walls = get_safe_walls()
current_items = get_safe_items()

clean_walls = {str(k): float(v) for k, v in current_walls.items()}
clean_items = []
for it in current_items:
    if isinstance(it, dict):
        clean_items.append({
            "id": str(it.get("id", "item")),
            "name": str(it.get("name", "가구")),
            "x": float(it.get("x", 0.0)),
            "y": float(it.get("y", 0.0)),
            "w": float(it.get("w", 1.0)),
            "l": float(it.get("l", 1.0)),
            "h": float(it.get("h", 0.8)),
            "rot": float(it.get("rot", 0.0)),
            "color": str(it.get("color", "#4D96FF"))
        })

# 5. 2D 평면도 컴포넌트 호출
canvas_data = interactive_canvas(
    house_w=house_w,
    house_l=house_l,
    walls=clean_walls,
    items=clean_items,
    key="interactive_floorplan"
)

# 6. 컴포넌트 수신 데이터 동기화
if canvas_data and isinstance(canvas_data, dict):
    if "walls" in canvas_data and isinstance(canvas_data["walls"], dict):
        for wk, wv in canvas_data["walls"].items():
            st.session_state["floorplan_walls"][wk] = float(wv)
            
    if "items" in canvas_data and isinstance(canvas_data["items"], list):
        for updated_it in canvas_data["items"]:
            if isinstance(updated_it, dict):
                for original_it in st.session_state["floorplan_items"]:
                    if isinstance(original_it, dict) and str(original_it.get("id")) == str(updated_it.get("id")):
                        original_it["x"] = float(updated_it.get("x", original_it["x"]))
                        original_it["y"] = float(updated_it.get("y", original_it["y"]))
                        original_it["rot"] = float(updated_it.get("rot", original_it.get("rot", 0.0)))

# --------------------------------------------------------------------------
# 7. 3D 입체 시각화 (Plotly)
# --------------------------------------------------------------------------
st.markdown("---")
st.subheader("🏗️ 3D 입체 건축 평면도 시각화 (실시간 반영)")

fig = go.Figure()

def create_box_3d(x, y, z, w, l, h, color, name):
    x_coords = [x, x + w, x + w, x, x, x + w, x + w, x]
    y_coords = [y, y, y + l, y + l, y, y, y + l, y + l]
    z_coords = [z, z, z, z, z + h, z + h, z + h, z + h]
    
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [4, 5, 1, 2, 5, 6, 2, 3, 0, 1, 2, 1]
    k = [6, 1, 5, 3, 6, 7, 3, 7, 1, 5, 7, 6]
    
    return go.Mesh3d(
        x=x_coords, y=y_coords, z=z_coords,
        i=i, j=j, k=k,
        color=color, opacity=0.9, name=name, showscale=False
    )

def create_wall_3d(x1, y1, x2, y2, height, thickness=0.15, color="#555555"):
    if x1 == x2:
        return create_box_3d(x1 - thickness/2, min(y1, y2), 0, thickness, abs(y2 - y1), height, color, "벽체")
    else:
        return create_box_3d(min(x1, x2), y1 - thickness/2, 0, abs(x2 - x1), thickness, height, color, "벽체")

# 바닥
fig.add_trace(go.Mesh3d(
    x=[0, house_w, house_w, 0, 0, house_w, house_w, 0],
    y=[0, 0, house_l, house_l, 0, 0, house_l, house_l],
    z=[0, 0, 0, 0, 0.05, 0.05, 0.05, 0.05],
    i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
    j=[4, 5, 1, 2, 5, 6, 2, 3, 0, 1, 2, 1],
    k=[6, 1, 5, 3, 6, 7, 3, 7, 1, 5, 7, 6],
    color="#EAEAEA", opacity=0.5, name="바닥"
))

# 3D 외벽
fig.add_trace(create_wall_3d(0, 0, house_w, 0, wall_h))
fig.add_trace(create_wall_3d(0, 0, 0, house_l, wall_h))
fig.add_trace(create_wall_3d(house_w, 0, house_w, house_l, wall_h))
fig.add_trace(create_wall_3d(0, house_l, house_w, house_l, wall_h))

# 3D 내벽
w = get_safe_walls()
fig.add_trace(create_wall_3d(0, w["y_mid"], house_w, w["y_mid"], wall_h))
fig.add_trace(create_wall_3d(w["x_mid1"], 0, w["x_mid1"], w["y_mid"], wall_h))
fig.add_trace(create_wall_3d(w["x_mid2"], w["y_mid"], w["x_mid2"], house_l, wall_h))
fig.add_trace(create_wall_3d(w["x_mid3"], w["y_mid"], w["x_mid3"], house_l, wall_h))
fig.add_trace(create_wall_3d(w["x_mid3"], w["y_bath"], house_w, w["y_bath"], wall_h))

# 3D 가구 (2D와 1:1 동기화)
for item in get_safe_items():
    if isinstance(item, dict):
        fig.add_trace(create_box_3d(
            x=float(item.get("x", 0.0)),
            y=float(item.get("y", 0.0)),
            z=0.05,
            w=float(item.get("w", 1.0)),
            l=float(item.get("l", 1.0)),
            h=float(item.get("h", 0.8)),
            color=str(item.get("color", "#4D96FF")),
            name=str(item.get("name", "가구"))
        ))

fig.update_layout(
    scene=dict(
        xaxis=dict(range=[0, house_w], title="가로 (m)"),
        yaxis=dict(range=[0, house_l], title="세로 (m)"),
        zaxis=dict(range=[0, wall_h + 1], title="높이 (m)"),
        aspectmode="data"
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    height=600
)

st.plotly_chart(fig, use_container_width=True)
