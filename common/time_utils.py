"""
시간 파싱/변환 공통 유틸리티

여러 모듈(hazel_nut_story, kora_valley 등)에서 반복되는
시간 문자열 → 분 단위 변환 로직을 통합한 모듈.
"""


def to_minutes(hhmm: str) -> int:
    """
    'HMM' 또는 'HHMM' 형식의 시간 문자열을 분(minute) 단위 정수로 변환.

    Examples:
        >>> to_minutes("930")   # 9시 30분
        570
        >>> to_minutes("1430")  # 14시 30분
        870
        >>> to_minutes("2400")  # 24시 00분
        1440
        >>> to_minutes("0")     # 0시 00분
        0
    """
    s = str(hhmm).strip()
    if not s.isdigit():
        return 0
    s = s.zfill(4)
    h, m = int(s[:-2]), int(s[-2:])
    return h * 60 + m


def parse_time(time_str: str) -> tuple[int, int]:
    """
    시간 문자열을 (시, 분) 튜플로 변환.

    Examples:
        >>> parse_time("930")
        (9, 30)
        >>> parse_time("1430")
        (14, 30)
        >>> parse_time("30")
        (0, 30)
    """
    time_num = int(time_str)
    if time_num < 100:
        return 0, time_num
    return time_num // 100, time_num % 100


def time_to_minutes(hour: int, minute: int) -> int:
    """
    시(hour)와 분(minute)을 총 분(minute) 단위로 변환.

    Examples:
        >>> time_to_minutes(14, 30)
        870
        >>> time_to_minutes(0, 45)
        45
    """
    return hour * 60 + minute
