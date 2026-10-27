import streamlit as st
import matplotlib.pyplot as plt

# 1. 페이지 레이아웃 및 헤더 설정 (국제 건축 표준 단위: m, m²)
st.set_page_config(page_title="건축 공간 가구 배치 및 동선 진단기", page_icon="📐", layout="centered")

st.title("📐 국제 건축 규격 기준: 주거 공간 가구 배치 & 쾌적도 진단기")
st.caption("국제 표준 단위(m, m²)와 건축 인체치수학(Ergonomics)을 바탕으로 공간 쾌적도 및 가구 배치 가이드를 제공합니다.")

st.divider()

# 2. 전체 프로그램 예외 처리 구조 (try-except)
try:
    # -------------------------------------------------------------
    # [입력 1] 방 치수 입력 (국제 표준 건축 단위: 미터 m)
    # -------------------------------------------------------------
    st.subheader("1. 방 치수 입력 (단위: m)")
    col_w, col_l = st.columns(2)
    
    with col_w:
        room_w = st.number_input("방의 가로 길이를 입력하세요 (m):", min_value=0.0, max_value=30.0, value=3.5, step=0.1)
    with col_l:
        room_l = st.number_input("방의 세로 길이를 입력하세요 (m):", min_value=0.0, max_value=30.0, value=3.0, step=0.1)

    # 입력값 유효성 검증 (예외 처리 1: 0 이하 수치 차단)
    if room_w <= 0 or room_l <= 0:
        st.warning("⚠️ 방의 가로 및 세로 길이는 0보다 큰 수치이어야 합니다.")
        st.stop()

    room_area = room_w * room_l
    st.info(f"📏 입력한 방의 전체 면적: **{room_area:.2f} m²**")

    st.divider()

    # -------------------------------------------------------------
    # [입력 2] 가구 선택 및 가구별 세부 치수 입력
    # -------------------------------------------------------------
    st.subheader("2. 배치할 가구 선택 및 크기 설정 (단위: m)")

    # 표준 건축 규격 프리셋 데이터베이스 (단위: m)
    DEFAULT_FURNITURE = {
        "싱글 침대": {"w": 1.0, "l": 2.0},
        "퀸 침대": {"w": 1.5, "l": 2.0},
        "1인용 책상": {"w": 1.2, "l": 0.7},
        "옷장/장롱": {"w": 1.2, "l": 0.6},
        "2인용 소파": {"w": 1.5, "l": 0.8},
        "서랍장/협탁": {"w": 0.6, "l": 0.5}
    }

    selected_preset = st.multiselect(
        "배치할 가구 항목을 선택하세요:",
        options=list(DEFAULT_FURNITURE.keys()),
        default=["싱글 침대", "1인용 책상", "옷장/장롱"]
    )

    total_furn_area = 0.0

    if selected_preset:
        st.markdown("##### ✏️ 선택 가구별 치수(가로x세로) 및 수량 조정")
        for idx, item in enumerate(selected_preset):
            default_w = DEFAULT_FURNITURE[item]["w"]
            default_l = DEFAULT_FURNITURE[item]["l"]

            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                fw = st.number_input(f"[{item}] 가로(m):", min_value=0.1, max_value=10.0, value=default_w, key=f"fw_{idx}")
            with f_col2:
                fl = st.number_input(f"[{item}] 세로(m):", min_value=0.1, max_value=10.0, value=default_l, key=f"fl_{idx}")
            with f_col3:
                fq = st.number_input(f"[{item}] 수량:", min_value=1, max_value=5, value=1, key=f"fq_{idx}")

            total_furn_area += (fw * fl * fq)

    # -------------------------------------------------------------
    # [연산 및 예외 처리] 면적 비교 검증
    # -------------------------------------------------------------
    if total_furn_area >= room_area:
        st.error("❌ 오류: 배치할 가구의 총 면적이 방 전체 면적 이상입니다. 방 크기를 늘리거나 가구를 줄여주세요.")
        st.stop()

    free_area = room_area - total_furn_area
    occupancy_ratio = (total_furn_area / room_area) * 100

    st.divider()

    # -------------------------------------------------------------
    # [출력 1] 공간 분석 및 쾌적도 진단 결과
    # -------------------------------------------------------------
    st.subheader("📊 3. 공간 분석 및 쾌적도 진단 결과")

    m1, m2, m3 = st.columns(3)
    m1.metric("방 전체 면적", f"{room_area:.2f} m²")
    m2.metric("가구 총 면적", f"{total_furn_area:.2f} m²")
    m3.metric("가구 점유 비율", f"{occupancy_ratio:.1f} %")

    # 건축 인체치수 기준 쾌적도 등급 판정 알고리즘
    st.markdown("### 🏠 쾌적도 등급 평가")
    if occupancy_ratio <= 30:
        st.success("🟢 **[1등급 - 매우 쾌적]** 이동 동선이 매우 여유롭습니다. 가구 배치 후에도 개방감이 뛰어납니다.")
    elif occupancy_ratio <= 40:
        st.info("🔵 **[2등급 - 적정 수준]** 국제 건축 표준 주거 배치 기준에 부합합니다. 이상적이고 효율적인 주거 환경입니다.")
    elif occupancy_ratio <= 50:
        st.warning("🟡 **[3등급 - 답답함]** 가구가 방의 절반가량을 차지합니다. 문/창문 앞 최소 통로 폭(0.6m)을 확인해야 합니다.")
    else:
        st.error("🔴 **[4등급 - 과밀/위험]** 이동 동선 침해 및 문 개폐 방해가 우려되므로 가구 수량을 줄이는 것을 권장합니다.")

    # visual 시각화 (Matplotlib 파이 차트)
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        [total_furn_area, free_area],
        labels=['가구 면적', '여유 동선 면적'],
        autopct='%1.1f%%',
        startangle=90,
        colors=['#ff9999', '#66b3ff']
    )
    ax.set_title("방 면적 대비 가구 점유 비율")
    st.pyplot(fig)

    st.divider()

    # -------------------------------------------------------------
    # [출력 2] 건축학 기준 가구 배치 솔루션 가이드
    # -------------------------------------------------------------
    st.subheader("💡 4. 건축학 기준 최적 가구 배치 가이드")

    aspect_ratio = room_w / room_l if room_l > 0 else 1.0

    st.markdown("##### 📌 1) 방 형태별 추천 구조")
    if 0.8 <= aspect_ratio <= 1.2:
        st.write("• **정사각형 형태의 방**: 방 중앙을 비우고 벽면을 따라 가구를 감싸듯 배치하는 **'L자형 벽면 밀착 배치'**가 유효합니다.")
    elif aspect_ratio > 1.2:
        st.write("• **가로가 긴 직사각형 방**: 방을 시각적으로 2개 영역(수면 존 / 학습·작업 존)으로 분할하여 배치하는 **'영역(Zoning) 분리 배치'**를 추천합니다.")
    else:
        st.write("• **세로가 긴 깊은 방**: 입구에서부터 동선이 막히지 않도록 큰 가구(침대, 옷장)를 안쪽 벽면에 집중 배치하는 **'일자형(I-Type) 동선'**이 적절합니다.")

    st.markdown("##### 📌 2) 건축 인체치수(Ergonomics) 동선 규칙")
    st.write("• **최소 이동 통로 폭**: 주 이동 동선은 최소 **0.6m (60cm)**, 주요 교차 동선은 **0.9m** 이상 확보해야 편하게 이동할 수 있습니다.")
    st.write("• **문 및 옷장 여유 공간**: 방문이나 옷장 문이 열리는 전면 공간은 최소 **0.8m** 이상 비워두어야 문이 부딪히지 않습니다.")

    st.markdown("##### 📌 3) 선택 가구별 위치 권가 솔루션")
    for item in selected_preset:
        if "침대" in item:
            st.write(f"• **{item}**: 방문에서 대각선으로 보이는 가장 안쪽 벽면에 머리 방향(Head)을 두고 배치하세요. (측면 통로 0.6m 확보 권장)")
        elif "책상" in item:
            st.write(f"• **{item}**: 창문을 정면에 두거나 side(측면)에 배치하여 채광을 활용하되, 의자를 뒤로 빼는 공간(최소 0.7m)을 확보하세요.")
        elif "옷장" in item:
            st.
