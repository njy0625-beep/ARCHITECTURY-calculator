import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# -------------------------------------------------------------
st.set_page_config(page_title="AI 3D 주거 공간 가구 배치 진단기", page_icon="🏠", layout="centered")

st.title("🏠 AI 기반 3D 주거 공간 배치 & 쾌적도 진단기")
st.caption("국제 건축 표준 단위(m, m², m³)와 가로·세로·높이 3차원 치수를 바탕으로 **3D 가구 배치 도면** 및 **공간 쾌적도**를 실시간 진단합니다.")

st.divider()

# -------------------------------------------------------------
# 2. 3D 입체 도형(Mesh3D) 생성 함수
# -------------------------------------------------------------
def create_3d_box(x0, y0, z0, dx, dy, dz, color, name):
    """Plotly 3D 렌더링을 위한 직육면체 가구 객체 생성"""
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    mesh = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=0.85,
        name=name,
        showscale=False,
        flatshading=True,
        hoverinfo="name"
    )
    return mesh

# -------------------------------------------------------------
# 3. 메인 프로그램
# -------------------------------------------------------------
try:
    # [입력 1] 방 치수 입력 (가로, 세로, 천장 높이)
    st.subheader("1. 방 공간 치수 입력 (단위: m)")
    col_w, col_l, col_h = st.columns(3)

    with col_w:
        room_w = st.number_input("방 가로 길이 (m):", min_value=0.0, max_value=20.0, value=3.5, step=0.1)
    with col_l:
        room_l = st.number_input("방 세로 길이 (m):", min_value=0.0, max_value=20.0, value=3.0, step=0.1)
    with col_h:
        room_h = st.number_input("천장 높이 (m):", min_value=1.5, max_value=5.0, value=2.4, step=0.1)

    # 예외 처리: 0 이하 치수 차단
    if room_w <= 0 or room_l <= 0 or room_h <= 0:
        st.warning("⚠️ 방의 가로, 세로, 천장 높이는 모두 0보다 큰 수치이어야 합니다.")
        st.stop()

    room_area = room_w * room_l
    room_vol = room_w * room_l * room_h
    st.info(f"📏 입력한 방 공간 정보: 바닥 면적 **{room_area:.2f} m²** | 전체 체적(부피) **{room_vol:.2f} m³**")

    st.divider()

    # [입력 2] 가구 선택 및 세부 치수 입력 (가로, 세로, 높이)
    st.subheader("2. 배치할 가구 선택 및 3D 치수 설정 (단위: m)")

    DEFAULT_FURNITURE = {
        "싱글 침대": {"w": 1.0, "l": 2.0, "h": 0.5, "color": "#4A90E2"},
        "퀸 침대": {"w": 1.5, "l": 2.0, "h": 0.5, "color": "#357ABD"},
        "1인용 책상": {"w": 1.2, "l": 0.7, "h": 0.75, "color": "#50E3C2"},
        "옷장/장롱": {"w": 1.2, "l": 0.6, "h": 2.0, "color": "#F5A623"},
        "2인용 소파": {"w": 1.5, "l": 0.8, "h": 0.8, "color": "#B8E986"},
        "서랍장/협탁": {"w": 0.6, "l": 0.5, "h": 0.7, "color": "#BD10E0"}
    }

    selected_preset = st.multiselect(
        "배치할 가구 항목을 선택하세요:",
        options=list(DEFAULT_FURNITURE.keys()),
        default=["싱글 침대", "1인용 책상", "옷장/장롱"]
    )

    total_furn_area = 0.0
    total_furn_vol = 0.0
    max_furn_h = 0.0
    furniture_list = []

    if selected_preset:
        st.markdown("##### ✏️ 선택 가구별 3D 규격(가로x세로x높이) 및 수량 조정")
        for idx, item in enumerate(selected_preset):
            preset = DEFAULT_FURNITURE[item]

            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                fw = st.number_input(f"[{item}] 가로(m):", min_value=0.1, max_value=10.0, value=preset["w"], key=f"fw_{idx}")
            with f_col2:
                fl = st.number_input(f"[{item}] 세로(m):", min_value=0.1, max_value=10.0, value=preset["l"], key=f"fl_{idx}")
            with f_col3:
                fh = st.number_input(f"[{item}] 높이(m):", min_value=0.1, max_value=5.0, value=preset["h"], key=f"fh_{idx}")
            with f_col4:
                fq = st.number_input(f"[{item}] 수량:", min_value=1, max_value=5, value=1, key=f"fq_{idx}")

            total_furn_area += (fw * fl * fq)
            total_furn_vol += (fw * fl * fh * fq)
            if fh > max_furn_h:
                max_furn_h = fh

            furniture_list.append({"name": item, "w": fw, "l": fl, "h": fh, "q": fq, "color": preset["color"]})

    # [예외 처리 1] 가구 높이가 방 천장 높이보다 높은 경우
    for furn in furniture_list:
        if furn["h"] > room_h:
            st.error(f"❌ 오류: [{furn['name']}]의 높이({furn['h']}m)가 방 천장 높이({room_h}m)보다 높아 배치할 수 없습니다!")
            st.stop()

    # [예외 처리 2] 가구 면적 초과
    if total_furn_area >= room_area:
        st.error("❌ 오류: 배치할 가구의 총 면적이 방 바닥 면적 이상입니다. 방 크기를 늘리거나 가구를 줄여주세요.")
        st.stop()

    occupancy_ratio = (total_furn_area / room_area) * 100
    ceiling_clearance = room_h - max_furn_h

    st.divider()

    # [출력 1] 공간 및 높이 분석 결과
    st.subheader("📊 3. 공간 및 높이(Height) 종합 진단 결과")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("방 바닥 면적", f"{room_area:.2f} m²")
    m2.metric("방 전체 부피(체적)", f"{room_vol:.2f} m³")
    m3.metric("가구 점유 비율", f"{occupancy_ratio:.1f} %")
    m4.metric("천장 여유 높이", f"{ceiling_clearance:.2f} m")

    st.markdown("### 🏠 쾌적도 등급 평가")
    if occupancy_ratio <= 30:
        st.success("🟢 **[1등급 - 매우 쾌적]** 이동 동선 및 상부 개방감이 매우 훌륭합니다.")
    elif occupancy_ratio <= 40:
        st.info("🔵 **[2등급 - 적정 수준]** 국제 건축 표준 주거 배치 기준에 부합합니다. 이상적인 주거 환경입니다.")
    elif occupancy_ratio <= 50:
        st.warning("🟡 **[3등급 - 답답함]** 가구가 방의 절반가량을 차지합니다. 통로 및 천장 시야 확보가 필요합니다.")
    else:
        st.error("🔴 **[4등급 - 과밀/위험]** 이동 동선 침해 및 시각적 답답함이 심하므로 가구 수량을 줄이는 것을 권장합니다.")

    st.divider()

    # -------------------------------------------------------------
    # [출력 2] AI 기반 3D 입체 가구 배치 도면
    # -------------------------------------------------------------
    st.subheader("🧊 4. 입력값 기반 AI 3D 가구 배치 도면")
    st.caption("💡 **가로 × 세로 × 높이** 치수가 3D 공간에 시각화됩니다. (마우스 드래그로 360도 회전 및 확대/축소 가능)")

    fig = go.Figure()

    # 바닥면
    fig.add_trace(go.Mesh3d(
        x=[0, room_w, room_w, 0],
        y=[0, 0, room_l, room_l],
        z=[0, 0, 0, 0],
        color="gainsboro",
        opacity=0.5,
        name="바닥"
    ))

    # 방 테두리 선
    lines_x = [0, room_w, room_w, 0, 0, 0, room_w, room_w, 0, 0, room_w, room_w, room_w, room_w, 0, 0]
    lines_y = [0, 0, room_l, room_l, 0, 0, 0, room_l, room_l, 0, 0, 0, room_l, room_l, room_l, room_l]
    lines_z = [0, 0, 0, 0, 0, room_h, room_h, room_h, room_h, room_h, 0, room_h, room_h, 0, 0, room_h]

    fig.add_trace(go.Scatter3d(
        x=lines_x, y=lines_y, z=lines_z,
        mode='lines',
        line=dict(color='black', width=3),
        showlegend=False,
        hoverinfo='none'
    ))

    # AI 생활 동선 및 높이 고려 배치 알고리즘
    clearance = 0.2

    def get_priority(item_name):
        if "침대" in item_name: return 1
        elif "옷장" in item_name: return 2
        elif "책상" in item_name: return 3
        else: return 4

    sorted_furniture = sorted(furniture_list, key=lambda x: get_priority(x["name"]))

    curr_x = clearance
    curr_y = clearance

    for furn in sorted_furniture:
        name = furn["name"]
        w, l, h = furn["w"], furn["l"], furn["h"]
        color = furn["color"]

        for q_idx in range(furn["q"]):
            if "침대" in name:
                x0 = room_w - w - clearance
                y0 = room_l - l - clearance
            elif "옷장" in name:
                x0 = clearance
                y0 = room_l - l - clearance if (room_l - l - clearance > 0) else clearance
            elif "책상" in name:
                x0 = clearance
                y0 = clearance
            else:
                if curr_x + w <= room_w - clearance:
                    x0 = curr_x
                    y0 = curr_y
                    curr_x += (w + clearance)
                else:
                    curr_x = clearance
                    curr_y += (l + clearance)
                    x0 = curr_x
                    y0 = curr_y

            x0 = max(0.1, min(x0, room_w - w - 0.1))
            y0 = max(0.1, min(y0, room_l - l - 0.1))

            # 3D 가구 박스 생성
            box_mesh = create_3d_box(x0, y0, 0, w, l, h, color, f"{name} ({q_idx+1})")
            fig.add_trace(box_mesh)

            # 가구 명칭 및 3D 치수(가로x세로x높이) 라벨 표기
            fig.add_trace(go.Scatter3d(
                x=[x0 + w/2],
                y=[y0 + l/2],
                z=[h + 0.15],
                text=[f"<b>{name}</b><br>({w}m × {l}m × H:{h}m)"],
                mode="text",
                showlegend=False,
                hoverinfo="text"
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='가로 (m)', range=[-0.5, room_w + 0.5]),
            yaxis=dict(title='세로 (m)', range=[-0.5, room_l + 0.5]),
            zaxis=dict(title='높이 (m)', range=[0, room_h + 0.5]),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.6, y=-1.6, z=1.2)
            )
        ),
        width=700,
        height=600,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------------------------------------------
    # [출력 3] 건축학 기준 높이 및 동선 가이드
    # -------------------------------------------------------------
    st.subheader("💡 5. 건축학 기준 높이(Height) 및 동선 솔루션")

    st.markdown("##### 📌 1) 천장 높이 및 시각적 개방감 분석")
    st.write(f"• **현재 천장 여유 높이**: 가장 높은 가구 대비 상부 여유 공간이 **{ceiling_clearance:.2f}m** 확보되어 있습니다.")
    st.write("• **높은 가구(옷장 등) 배치 규칙**: 높이 1.8m 이상의 키 높은 가구는 방문 근처에 배치하면 입구에서 답답함을 유발하므로, 안쪽 구석 벽면에 붙여 시야 간섭을 줄였습니다.")

    st.markdown("##### 📌 2) 건축 인체치수(Ergonomics) 동선 규칙")
    st.write("• **최소 이동 통로 폭**: 주 이동 동선은 최소 **0.6m (60cm)**, 주요 교차 동선은 **0.9m** 이상 확보해야 편하게 이동할 수 있습니다.")
    st.write("• **문 및 옷장 여유 공간**: 방문이나 옷장 문이 열리는 전면 공간은 최소 **0.8m** 이상 비워두어야 문이 부딪히지 않습니다.")

except ValueError:
    st.error("❌ 올바른 수치 형식의 숫자를 입력해 주세요.")
except Exception as e:
    st.error(f"❌ 프로그램 실행 중 예기치 않은 오류가 발생했습니다: {e}")
