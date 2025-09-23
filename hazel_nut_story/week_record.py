from matplotlib import font_manager as fm
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
import matplotlib.image as mpimg
from PIL import Image, ImageDraw, ImageFont
import io
from matplotlib import font_manager as _fm

# ✅ 기본 설정
TEMPLATE_PATH = "hazel_nut_story/weekly_template.jpg"   # 배경 이미지 파일명
DATE_FONT_PATH = "/Users/cheonseungbeom/Desktop/CSB/그 외/BinggraeSamanco-Bold.otf"
FONT_PATH = "/Users/cheonseungbeom/Desktop/CSB/그 외/JejuHallasanOTF.otf"  # 폰트 파일 경로

# ✅ 시간 파싱 함수
def parse_minutes(t: str) -> int:
    t = t.zfill(4)
    h, m = int(t[:-2]), int(t[-2:])
    return h * 60 + m

COLOR_LIST = ["#FA7D7C", "#F9AE7D", "#F7FC7F", "#7DF97E", "#80E0FA", "#7D7DFA", "#CA7CFA"]

# 활동명 → 카테고리 매핑(우선순위대로, 구체적인 것 먼저)
CATEGORY_MAP = OrderedDict([
    ("FBA Quant FE세션", "퀀트"),
    ("퀀트 과제", "퀀트"),
    ("퀀트 공부", "퀀트"),
    ("코테 공부", "코딩"),
    ("코딩 작업", "코딩"),
    ("언어 공부", "언어"),
    ("헬스", "헬스"),
    ("글쓰기/읽기", "글쓰기"),
    ("글쓰기", "글쓰기"),
    ("유익한 영상", "유익한 영상"),
    ("GTC Meeting", "GTC"),
    ("GTC 일", "GTC"),
    ("GTC", "GTC"),
    ("코라밸리 미팅", "코라밸리"),
    ("코라밸리", "코라밸리"),
    ("BOTA 질문답변", "BOTA"),
])

# ====== 입력 텍스트(그대로 붙여넣기) ======
weekly_text = """
2025년 8월 18일 월요일
오전 1:25 천승범 토크 000 130
오전 9:04 천승범 주식 공부 750 910
오전 9:39 천승범 헬스 930 1030
오후 7:34 천승범 독서 1800 1940
오후 9:34 천승범 언어 공부 2110 2130
오후 9:45 천승범 주식 공부 2130 2150
오후 9:45 천승범 유익한 영상 2150 2210
2025년 8월 19일 화요일
오전 6:55 천승범 주식공부 640 700
오전 7:02 천승범 TOEIC 공부 700 840
오전 10:45 천승범 독서 1040 1120
오후 4:59 천승범 헬스 1130 1230
오후 6:58 천승범 지원서 작성 1850 2020
2025년 8월 20일 수요일
오전 1:58 천승범 지원서 작성 1230 1400
오후 12:22 천승범 주식 공부 1200 1230
오후 2:43 천승범 지원서 작성 1430 1530
오후 6:54 천승범 유익한 영상 1850 1930
오후 11:45 천승범 헬스 1950 2050
오후 11:45 천승범 언어 공부 2330 2350
오후 11:50 천승범 주식 공부 2350 2400
2025년 8월 21일 목요일
오전 2:40 천승범 TOEIC 공부 000 240
오후 12:27 천승범 주식 공부 1140 1210
오후 12:27 천승범 퀀트 공부 1210 1500
2025년 8월 22일 금요일
오전 4:58 천승범 주식 공부 450 500
오전 5:37 천승범 GDGoC 일 500 540
오전 6:40 천승범 퀀트 공부 540 640
오후 3:43 천승범 헬스 1230 1330
오후 4:44 천승범 추가 서치 1600 1650
오후 4:50 천승범 퀀트 공부 1650 1730
오후 9:26 천승범 유익한 영상 1800 1830
오후 9:26 천승범 GDGoC 미팅 1900 2120
오후 9:28 천승범 유익한 영상 2120 2210
오전 4:34 천승범 언어 공부 2300 2320
2025년 8월 23일 토요일
오전 4:36 천승범 인스타 제작 330 440
오후 3:52 천승범 주식 공부 1500 1530
오후 3:52 천승범 퀀트 공부 1530 1730
오후 8:19 천승범 FBA Quant FE세션 2000 2040
오후 9:29 천승범 코라밸리 미팅 2040 2150
오후 9:48 천승범 유익한 영상 2150 2200
오후 10:02 천승범 언어 공부 2200 2220
2025년 8월 24일 일요일
오전 1:29 천승범 주식 공부 1410 1440
오후 2:58 천승범 퀀트 공부 1440 1810
오후 10:50 천승범 풋살 2000 2200
오후 10:51 천승범 FBA Quant AP세션 2200 2300
오후 10:52 천승범 언어 공부 2300 2320
"""

def map_category(plan: str) -> str:
    for key, cat in CATEGORY_MAP.items():
        if key in plan:
            return cat
    return plan  # 매핑 실패 시 활동명을 그대로 카테고리로

def generate_weekly_planner(weekly_text):
    # 몇 번째 주인지 계산
    week_num = 1  # 예시에서는 첫째주로 고정
    # 타이틀 생성
    title = "08.18 ~ 08.24"
    
    # 플래너 이미지 불러오기
    image = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(image)
    date_font = ImageFont.truetype(DATE_FONT_PATH, size=54)
    title_font = ImageFont.truetype(FONT_PATH, size=28)
    times_font = ImageFont.truetype(FONT_PATH, size=19)
    
    # 총 집중 시간 계산
    total_minutes = 0
    week_lines = weekly_text.strip().splitlines()
    for line in week_lines:
        parts = line.strip().split()
        if len(parts) >= 6:
            start, end = parts[-2], parts[-1]
            dur = parse_minutes(end) - parse_minutes(start)
            if dur > 0:
                total_minutes += dur
                
    # # 지난 4주 데이터(분) 넣기
    # last4_weeks_minutes = [4350, 3030, 3000]  # <- 여기에 최근 4주의 총집중시간(분) 입력
    # trend_minutes = last4_weeks_minutes + [total_minutes]
    # 타이틀/총 집중 시간(왼쪽 정렬)
    draw.text((160, 150), title, font=date_font, fill="black")
    draw.text((182.1, 272.5), "요일별 집중 시간", font=title_font, fill="black")
    draw.line((169.2, 330.3, 910.8, 330.3), fill="#d9d9d9", width=2)  # 구분선
    text1 = "총 집중 시간: "
    text2 = f"{total_minutes}"
    text3 = " 분"

    # 첫 번째 텍스트 (검정)
    draw.text((182.1, 351.5), text1, font=times_font, fill="black")

    # 두 번째 텍스트 (보라색)
    offset_x = 182.1 + draw.textlength(text1, font=times_font)
    draw.text((offset_x, 351.5), text2, font=times_font, fill="#c348e6")
    
    # 세 번째 텍스트 (검정)
    offset_x += draw.textlength(text2, font=times_font)
    draw.text((offset_x, 351.5), text3, font=times_font, fill="black")
    
    # --- 요일별 집중시간 막대그래프 (절대좌표) ---
    # 1) 데이터: 월~일 분 단위 값만 채워줘
    mon, tue, wed, thu, fri, sat, sun = 280, 360, 210, 480, 520, 300, 140  # <- 네 값으로 수정
    day_values = [mon, tue, wed, thu, fri, sat, sun]

    # 2) 막대 중심 x좌표(예: 228.3, 326.6 간격이 98.3이면 이렇게 7개)
    bar_centers = [249.8+13.1, 348.1+13.1, 448.3+13.1, 546.7+13.1, 645+13.1, 743.3+13.1, 840.3+13.1]  # ← 필요시 직접 값 넣기
    BAR_W = 35  # 막대 폭(px)
    BAR_RADIUS = 6  # 모서리 둥근 정도
    BAR_FILL = "#d6b0e1"     # 채움색
    BAR_EDGE = "#9e72b0"     # 테두리색
    BAR_EDGE_W = 2           # 테두리 두께

    # 3) y 스케일: 0분 -> 607.5, 600분 -> 412.6
    Y_AT_0 = 607.5
    Y_AT_600 = 412.6
    Y_MIN_VAL, Y_MAX_VAL = 0, 600

    def y_from_value(v):
        # 0~600 클램프 후 선형 보간
        v = max(Y_MIN_VAL, min(Y_MAX_VAL, v))
        return Y_AT_0 + (Y_AT_600 - Y_AT_0) * (v / (Y_MAX_VAL - Y_MIN_VAL))

    # 4) 막대만 그림
    for cx, val in zip(bar_centers, day_values):
        top_y = y_from_value(val)
        draw.rounded_rectangle(
            [cx - BAR_W/2, top_y, cx + BAR_W/2, Y_AT_0],
            radius=BAR_RADIUS,
            fill=BAR_FILL,
            outline=BAR_EDGE,
            width=BAR_EDGE_W
        )
        
    draw.text((182.1, 757.6), "카테고리별", font=title_font, fill="black")
    draw.line((169.2, 820.6, 910.8, 820.6), fill="#d9d9d9", width=2)  # 구분선

    # 1) 카테고리 총분 집계
    cat_minutes = defaultdict(int)
    for line in weekly_text.strip().splitlines():
        parts = line.strip().split()
        if len(parts) >= 6 and parts[-2].isdigit() and parts[-1].isdigit():
            plan = " ".join(parts[3:-2])
            dur = parse_minutes(parts[-1]) - parse_minutes(parts[-2])
            if dur > 0:
                cat = map_category(plan)
                cat_minutes[cat] += dur

    # 2) 상위 6개만 추림 (기타 제외)
    sorted_cats = sorted(cat_minutes.items(), key=lambda x: x[1], reverse=True)
    top6 = sorted_cats[:6]
    pie_labels = [c for c, _ in top6]
    pie_sizes  = [m for _, m in top6]
    pie_colors = COLOR_LIST[:len(top6)]

    # 3) Matplotlib로 투명 배경 파이 이미지 만들기
    pie_left, pie_top, pie_w, pie_h = 324.8, 857.6, 430.3, 430.3  # 위치/크기(px)
    dpi = 200
    fig_w_in, fig_h_in = pie_w / dpi, pie_h / dpi

    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in), dpi=dpi)
    fig.patch.set_alpha(0)  # 투명

    # 폰트(퍼센트 텍스트용)
    pie_font = _fm.FontProperties(fname=FONT_PATH, size=8)

    wedges, _, autotexts = ax.pie(
        pie_sizes,
        colors=pie_colors,
        startangle=90,            # 12시 시작
        counterclock=False,       # 시계 방향
        autopct=lambda pct: f"{pct:.0f}%" if pct >= 10 else "",
        wedgeprops=dict(width=1.0, edgecolor="white"),
        textprops=dict(color="#b4b4b4", fontproperties=pie_font),
    )
    ax.set_aspect('equal')
    ax.set_axis_off()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)

    # 4) PIL 이미지로 붙여넣기
    pie_img = Image.open(buf).convert("RGBA")
    # bbox_inches='tight' 때문에 실제 픽셀 크기가 약간 달 수 있어, 그대로 붙여도 되고 정확히 맞추려면 resize
    pie_img = pie_img.resize((int(pie_w), int(pie_h)))
    image.paste(pie_img, (int(pie_left), int(pie_top)), pie_img)
    
    # --- 상위 6개 카테고리 상세(계획명 / % / 분) 출력 ---
    rows = sorted_cats[:6]  # (카테고리명, 분)
    total_cat_minutes = sum(m for _, m in rows) or 1  # ← 분모: 상위 6개 합

    # 고정 좌표
    X_NAME = 219.2
    X_PCT  = 673.7
    X_MIN  = 837.2
    Y0     = 1330.5      # 1번째 줄 y
    Y_STEP = 68.0        # 줄 간격 (2번째: 1391.5)

    for i, (label, mins) in enumerate(rows):
        y = Y0 + i * Y_STEP
        pct = mins / total_cat_minutes * 100

        # 계획(카테고리)명
        draw.text((X_NAME, y), label, font=times_font, fill="#545454")
        # 퍼센트(정수 %)
        draw.text((X_PCT,  y), f"{pct:.0f}%", font=times_font, fill="#545454")
        # 분(천단위 콤마)
        draw.text((X_MIN,  y), f"{mins:}분", font=times_font, fill="#545454")

    image.save("hazel_nut_story/weekly_record/2025_08/august_week3.png")


# ✅ 테스트 입력 실행 예시
if __name__ == "__main__":
    generate_weekly_planner(weekly_text)