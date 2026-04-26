"""
주간 기록 플래너 이미지 생성

주간 활동 데이터를 파싱하여 다음을 포함한 플래너 이미지를 생성합니다:
- 요일별 집중 시간 막대그래프
- 카테고리별 원형 차트
- 상위 6개 카테고리 상세 내역

사용법:
    python week_record.py                # 기본 weekly_input.txt 사용
    python week_record.py weekly_data.txt # 원하는 데이터 파일 지정
"""

import io
import os
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import font_manager as _fm
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from common.config import COLOR_7, FONT_HALLASAN, FONT_SAMANCO
from common.time_utils import to_minutes
from common.ai_categorizer import map_category

# =============================
# 경로 설정
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "weekly_template.jpg")
DEFAULT_INPUT = os.path.join(BASE_DIR, "weekly_input.txt")




def parse_weekly_data(text):
    """
    주간 텍스트 데이터에서 요일별/카테고리별 집중 시간을 파싱합니다.

    Returns:
        tuple: (total_minutes, day_values, cat_minutes)
    """
    total_minutes = 0
    day_minutes = defaultdict(int)  # 요일(0=월~6=일) → 분
    cat_minutes = defaultdict(int)  # 카테고리 → 분
    current_date = None

    date_pat = re.compile(r"(\d{4})년\s+(\d{1,2})월\s+(\d{1,2})일")

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        m = date_pat.search(line)
        if m:
            y, mo, d = map(int, m.groups())
            current_date = datetime(y, mo, d)
            continue

        parts = line.split()
        if len(parts) >= 6 and parts[-2].isdigit() and parts[-1].isdigit():
            dur = to_minutes(parts[-1]) - to_minutes(parts[-2])
            if dur > 0:
                total_minutes += dur
                plan = " ".join(parts[3:-2])
                cat = map_category(plan)
                cat_minutes[cat] += dur
                if current_date:
                    day_minutes[current_date.weekday()] += dur

    # 월~일 순서로 정렬
    day_values = [day_minutes.get(i, 0) for i in range(7)]
    return total_minutes, day_values, cat_minutes


def generate_weekly_planner(text, title="08.18 ~ 08.24", output_path=None):
    """
    주간 플래너 이미지를 생성합니다.

    Args:
        text: 주간 활동 텍스트 데이터
        title: 주간 타이틀 (예: "08.18 ~ 08.24")
        output_path: 저장 경로
    """
    if output_path is None:
        output_path = os.path.join(BASE_DIR, "weekly_record", "latest.png")

    total_minutes, day_values, cat_minutes = parse_weekly_data(text)

    # 플래너 이미지 불러오기
    image = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(image)
    date_font = ImageFont.truetype(FONT_SAMANCO, size=54)
    title_font = ImageFont.truetype(FONT_HALLASAN, size=28)
    times_font = ImageFont.truetype(FONT_HALLASAN, size=19)

    # 타이틀/총 집중 시간
    draw.text((160, 150), title, font=date_font, fill="black")
    draw.text((182.1, 272.5), "요일별 집중 시간", font=title_font, fill="black")
    draw.line((169.2, 330.3, 910.8, 330.3), fill="#d9d9d9", width=2)

    text1, text2, text3 = "총 집중 시간: ", f"{total_minutes}", " 분"
    draw.text((182.1, 351.5), text1, font=times_font, fill="black")
    offset_x = 182.1 + draw.textlength(text1, font=times_font)
    draw.text((offset_x, 351.5), text2, font=times_font, fill="#c348e6")
    offset_x += draw.textlength(text2, font=times_font)
    draw.text((offset_x, 351.5), text3, font=times_font, fill="black")

    # --- 요일별 집중시간 막대그래프 ---
    bar_centers = [249.8 + 13.1, 348.1 + 13.1, 448.3 + 13.1, 546.7 + 13.1, 645 + 13.1, 743.3 + 13.1, 840.3 + 13.1]
    BAR_W, BAR_RADIUS = 35, 6
    BAR_FILL, BAR_EDGE, BAR_EDGE_W = "#d6b0e1", "#9e72b0", 2
    Y_AT_0, Y_AT_600 = 607.5, 412.6

    def y_from_value(v):
        v = max(0, min(600, v))
        return Y_AT_0 + (Y_AT_600 - Y_AT_0) * (v / 600)

    for cx, val in zip(bar_centers, day_values):
        top_y = y_from_value(val)
        draw.rounded_rectangle(
            [cx - BAR_W / 2, top_y, cx + BAR_W / 2, Y_AT_0],
            radius=BAR_RADIUS, fill=BAR_FILL, outline=BAR_EDGE, width=BAR_EDGE_W,
        )

    # --- 카테고리별 원형 차트 ---
    draw.text((182.1, 757.6), "카테고리별", font=title_font, fill="black")
    draw.line((169.2, 820.6, 910.8, 820.6), fill="#d9d9d9", width=2)

    sorted_cats = sorted(cat_minutes.items(), key=lambda x: x[1], reverse=True)
    top6 = sorted_cats[:6]
    pie_labels = [c for c, _ in top6]
    pie_sizes = [m for _, m in top6]
    pie_colors = COLOR_7[: len(top6)]

    # Matplotlib 투명 배경 파이 이미지
    pie_left, pie_top, pie_w, pie_h = 324.8, 857.6, 430.3, 430.3
    dpi = 200
    fig, ax = plt.subplots(figsize=(pie_w / dpi, pie_h / dpi), dpi=dpi)
    fig.patch.set_alpha(0)

    pie_font = _fm.FontProperties(fname=FONT_HALLASAN, size=8)

    wedges, _, autotexts = ax.pie(
        pie_sizes,
        colors=pie_colors,
        startangle=90,
        counterclock=False,
        autopct=lambda pct: f"{pct:.0f}%" if pct >= 10 else "",
        wedgeprops=dict(width=1.0, edgecolor="white"),
        textprops=dict(color="#b4b4b4", fontproperties=pie_font),
    )
    ax.set_aspect("equal")
    ax.set_axis_off()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)

    pie_img = Image.open(buf).convert("RGBA")
    pie_img = pie_img.resize((int(pie_w), int(pie_h)))
    image.paste(pie_img, (int(pie_left), int(pie_top)), pie_img)

    # --- 상위 6개 카테고리 상세 ---
    rows = sorted_cats[:6]
    total_cat_minutes = sum(m for _, m in rows) or 1

    X_NAME, X_PCT, X_MIN = 219.2, 673.7, 837.2
    Y0, Y_STEP = 1330.5, 68.0

    for i, (label, mins) in enumerate(rows):
        y = Y0 + i * Y_STEP
        pct = mins / total_cat_minutes * 100
        draw.text((X_NAME, y), label, font=times_font, fill="#545454")
        draw.text((X_PCT, y), f"{pct:.0f}%", font=times_font, fill="#545454")
        draw.text((X_MIN, y), f"{mins:}분", font=times_font, fill="#545454")

    # 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
    print(f"✅ {output_path} 저장 완료")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    with open(input_file, "r", encoding="utf-8") as f:
        weekly_text = f.read()
    generate_weekly_planner(weekly_text)