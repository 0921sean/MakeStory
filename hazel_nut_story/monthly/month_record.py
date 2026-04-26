"""
월간 집중 시간 인스타 스토리 이미지 생성

지정한 월의 활동 데이터를 파싱하여 상위 6개 카테고리 + 기타로 분류,
원형 차트와 상세 내역이 포함된 인스타 스토리용 이미지를 생성합니다.

사용법:
    python month_record.py           # july.txt 기본 사용
    python month_record.py data.txt  # 원하는 데이터 파일 지정
"""

import os
import sys
from collections import defaultdict

import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.patches import Circle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from common.config import FONT_SAMANCO, COLOR_7
from common.time_utils import to_minutes
from common.ai_categorizer import map_category

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "july.txt")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "insta_story_final.png")

font_prop = fm.FontProperties(fname=FONT_SAMANCO)


def load_activity_data(filepath):
    """데이터 파일을 읽어 계획별 총 시간(분)을 계산합니다."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    plan_durations = defaultdict(int)
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 6:
            plan = " ".join(parts[3:-2])
            start, end = parts[-2], parts[-1]
            duration = to_minutes(end) - to_minutes(start)
            if duration > 0:
                cat = map_category(plan)
                plan_durations[cat] += duration

    return plan_durations


def generate_monthly_story(plan_durations, title="2025년 7월", output_path=None):
    """월간 인스타 스토리 이미지를 생성합니다."""
    if output_path is None:
        output_path = OUTPUT_PATH

    # 상위 6개 + 기타 분류
    sorted_plans = sorted(plan_durations.items(), key=lambda x: x[1], reverse=True)
    top6 = sorted_plans[:6]
    others = sorted_plans[6:]
    labels = [x[0] for x in top6] + ["기타"]
    sizes = [x[1] for x in top6] + [sum(x[1] for x in others)]
    total = sum(sizes)
    percentages = [s / total * 100 for s in sizes]
    colors = COLOR_7

    # 인스타 스토리 캔버스 생성
    fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
    ax = plt.subplot2grid((20, 1), (1, 0), rowspan=8)

    # 원형 차트 (12시부터 시계 방향, 흰색 테두리)
    wedges, _, autotexts = ax.pie(
        sizes,
        colors=colors,
        startangle=90,
        counterclock=False,
        autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
        wedgeprops=dict(width=1.0, edgecolor="white"),
        textprops=dict(color="#666666", fontsize=18),
    )
    ax.set_aspect("equal")

    # 상단 제목
    fig.text(0.5, 0.96, title, ha="center", va="center", fontsize=30, weight="bold", fontproperties=font_prop)
    fig.text(0.5, 0.915, f"총 집중 시간: {total:,}분", ha="center", fontsize=20, fontproperties=font_prop)

    # 하단 항목 정렬 (색상 원 + 항목명 + 백분율 + 분)
    y_start = 0.37
    y_step = 0.048
    left_circle_x = 0.18
    left_text_x = 0.21
    right_pct_x = 0.65
    right_min_x = 0.83
    line_left = 0.15
    line_right = 0.85

    for i, (label, pct, mins, color) in enumerate(zip(labels, percentages, sizes, colors)):
        y = y_start - i * y_step
        fig.patches.append(Circle((left_circle_x, y), 0.01, color=color, transform=fig.transFigure, figure=fig))
        fig.text(left_text_x, y, label, fontsize=20, color="#666666", ha="left", fontproperties=font_prop)
        fig.text(right_pct_x, y, f"{pct:.0f}%", fontsize=20, color="#666666", ha="right", fontproperties=font_prop)
        fig.text(right_min_x, y, f"{mins:,}  분", fontsize=20, color="#666666", ha="right", fontproperties=font_prop)
        fig.lines.append(
            Line2D([line_left, line_right], [y - 0.018, y - 0.018], lw=0.5, color="#dddddd", transform=fig.transFigure)
        )

    plt.savefig(output_path, bbox_inches="tight", dpi=100)
    plt.show()
    print(f"✅ {output_path} 저장 완료")


if __name__ == "__main__":
    data_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_FILE
    plan_durations = load_activity_data(data_file)
    generate_monthly_story(plan_durations)