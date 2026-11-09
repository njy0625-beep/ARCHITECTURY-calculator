import os
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(page_title="AI 건축 평면도 & 3D 스마트 인테리어", layout="wide")

# 1. 2D 커스텀 컴포넌트 불러오기
parent_dir = os.path.dirname(os.path.abspath(__file__))
component_dir = os.path.join(parent_dir, "canvas_component")
interactive_canvas = components.declare_component("interactive_canvas", path=component_dir)

# 2. 초기 세션 데이터 설정
if "walls" not in st.session_state:
    st.session_state.walls = {
        "y_mid": 4.4,
        "x_mid1": 5.0,
        "x_mid2": 3.8,
        "x_mid3": 7.5,
        "y_bath": 6.4
    }

if "items" not in st.session_state:
    st.session_state.items = [
        {"id": "sofa", "name": "거실 소파", "x": 0.8, "y": 0.8, "w": 2.4, "l": 1.2, "h": 0.9, "rot": 0.0, "color": "#E74C3C"},
        {"id": "tv", "name": "TV장", "x": 0.8, "y": 2.8, "w": 1.8, "l": 0.6, "h": 0.6, "rot": 0.0, "color": "#3498DB"},
        {"id": "bed", "name": "안방 침대", "x": 5.5, "y": 0.8, "w": 2.0, "l": 2.0, "h": 1.1, "rot": 0.0, "color": "#9B59B6"},
        {"id": "table", "name": "주방 식탁", "x": 4.2, "y": 4.8, "w": 1.8, "l": 1.1, "h": 0.8, "rot": 0.0, "color": "#F39C12"},
        {"id": "fridge", "name": "냉장고", "x": 7.8, "y": 4.6, "w": 1.0, "l": 1.0, "h": 1.8, "rot": 0.0, "color": "#2ECC71"},
        {"id": "desk", "name": "작은방 책상", "x": 0.8, "y": 4.8, "w": 1.4, "l": 0.9, "h": 0.75, "rot": 0.0, "color": "#1ABC9C"}
    ]

# 3. 페이지 상단 입력 컨트롤
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

# JSON 직렬화 오류 방지를 위한 타입 정제 함수
clean_walls = {str(k): float(v) for k, v in st.session_state.walls.items()}
clean_items = []
for it in st.session_state.items:
    clean_items.append({
        "id": str(it["id"]),
        "name": str(it["name"]),
        "x": float(it["x"]),
        "y": float(it["y"]),
        "w": float(it["w"]),
        "l": float(it["l"]),
        "h": float(it.get("h", 0.8)),
        "rot": float(it.get("rot", 0.0)),
        "color": str(it["color"])
    })

# 4. 2D 평면도 캔버스 컴포넌트 실행
canvas_data = interactive_canvas(
    house_w=house_w,
    house_l=house_l,
    walls=clean_walls,
    items=clean_items,
    key="interactive_floorplan"
)

# 5. 2D에서 데이터 수신 시 세션 상태 업데이트
if canvas_data and isinstance(canvas_data, dict):
    if "walls" in canvas_data and isinstance(canvas_data["walls"], dict):
        for wk, wv in canvas_data["walls"].items():
            st.session_state.walls[wk] = float(wv)
            
    if "items" in canvas_data and isinstance(canvas_data["items"], list):
        for updated_it in canvas_data["items"]:
            for original_it in st.session_state.items:
                if str(original_it["id"]) == str(updated_it.get("id")):
                    original_it["x"] = float(updated_it["x"])
                    original_it["y"] = float(updated_it["y"])
                    original_it["rot"] = float(updated_it.get("rot", 0.0))

# --------------------------------------------------------------------------
# 6. 3D 입체 모델 생성 (2D와 1:1 동일한 내벽 및 가구 위치 반영)
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
w = st.session_state.walls
fig.add_trace(create_wall_3d(0, w["y_mid"], house_w, w["y_mid"], wall_h))
fig.add_trace(create_wall_3d(w["x_mid1"], 0, w["x_mid1"], w["y_mid"], wall_h))
fig.add_trace(create_wall_3d(w["x_mid2"], w["y_mid"], w["x_mid2"], house_l, wall_h))
fig.add_trace(create_wall_3d(w["x_mid3"], w["y_mid"], w["x_mid3"], house_l, wall_h))
fig.add_trace(create_wall_3d(w["x_mid3"], w["y_bath"], house_w, w["y_bath"], wall_h))

# 3D 가구 (2D와 1:1 대응)
for item in st.session_state.items:
    fig.add_trace(create_box_3d(
        x=float(item["x"]),
        y=float(item["y"]),
        z=0.05,
        w=float(item["w"]),
        l=float(item["l"]),
        h=float(item.get("h", 0.8)),
        color=str(item["color"]),
        name=str(item["name"])
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
