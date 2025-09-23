# -*- coding: utf-8 -*-
# july.txt로부터 최근 4개 ISO 주(월~일 기준) 총 집중 시간(분)을 계산해 리스트로 출력

import re
from datetime import datetime
from collections import defaultdict, OrderedDict
from pathlib import Path

# JULY_FILE = "july.txt"  # 파일 경로만 맞춰주면 됨

date_pat = re.compile(r"(\d{4})년\s+(\d{1,2})월\s+(\d{1,2})일")

def to_minutes(hhmm: str) -> int:
    """'HMM', 'HHMM', '2400' 같은 문자열을 분으로 변환"""
    s = hhmm.strip()
    if not s.isdigit():
        return 0
    s = s.zfill(4)
    h, m = int(s[:-2]), int(s[-2:])
    return h * 60 + m

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
                # 지정한 달만 포함
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
            continue  # 이상치 무시

        iso_year, iso_week, _ = current_date.isocalendar()
        week_key = (iso_year, iso_week)
        week_minutes[week_key] += dur

    # (연, 주) 정렬 후 최근 4개 반환
    sorted_weeks = sorted(week_minutes.items())  # 오래된 -> 최신
    last4 = sorted_weeks[-4:] if len(sorted_weeks) >= 4 else sorted_weeks

    # 보기 좋은 라벨과 함께 출력용 데이터 구성
    labels = [f"{y}-W{w}" for (y, w), _ in last4]
    minutes = [mins for _, mins in last4]
    return labels, minutes

if __name__ == "__main__":
    labels, minutes = weekly_minutes_from_file(Path("hazel_nut_story/july.txt"), target_year=2025, target_month=7)

    # 결과 출력
    print("주차 라벨:", labels)
    print("각 주 총 집중 시간(분):", minutes)

    # 트렌드 그래프에 바로 붙여넣기 쉬운 한 줄
    print("last4_weeks_minutes =", minutes)