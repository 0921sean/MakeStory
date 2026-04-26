"""
주차별 총 집중 시간 계산

july.txt 로부터 특정 월의 ISO 주(월~일) 단위 총 집중 시간(분)을 계산합니다.
"""

import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from common.time_utils import to_minutes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

date_pat = re.compile(r"(\d{4})년\s+(\d{1,2})월\s+(\d{1,2})일")


def weekly_minutes_from_file(path: Path, target_year: int = 2025, target_month: int = 7):
    """
    파일을 읽어 (연, ISO주) 단위로 총 분을 집계.
    target_year/target_month로 필터(해당 월의 날짜만 포함).
    """
    text = path.read_text(encoding="utf-8")
    current_date = None
    week_minutes = defaultdict(int)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # 날짜 라인인지 확인
        m = date_pat.search(line)
        if m:
            y, mo, d = map(int, m.groups())
            try:
                dt = datetime(y, mo, d)
            except ValueError:
                current_date = None
            else:
                current_date = dt if (dt.year == target_year and dt.month == target_month) else None
            continue

        # 활동 라인: 마지막 두 토큰이 시작/끝 시간(숫자)이라고 가정
        if current_date is None:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        start_str, end_str = parts[-2], parts[-1]
        if not (start_str.isdigit() and end_str.isdigit()):
            continue

        start_min = to_minutes(start_str)
        end_min = to_minutes(end_str)
        dur = end_min - start_min
        if dur <= 0:
            continue

        iso_year, iso_week, _ = current_date.isocalendar()
        week_key = (iso_year, iso_week)
        week_minutes[week_key] += dur

    # (연, 주) 정렬 후 최근 4개 반환
    sorted_weeks = sorted(week_minutes.items())
    last4 = sorted_weeks[-4:] if len(sorted_weeks) >= 4 else sorted_weeks

    labels = [f"{y}-W{w}" for (y, w), _ in last4]
    minutes = [mins for _, mins in last4]
    return labels, minutes


if __name__ == "__main__":
    july_path = Path(os.path.join(BASE_DIR, "july.txt"))
    labels, minutes = weekly_minutes_from_file(july_path, target_year=2025, target_month=7)

    print("주차 라벨:", labels)
    print("각 주 총 집중 시간(분):", minutes)
    print("last4_weeks_minutes =", minutes)