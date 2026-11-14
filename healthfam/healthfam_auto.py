"""
헬스팸 자동 정산

맥 카카오톡의 로컬 DB에서 직전 주(월~일) 채팅을 읽어 멤버별 운동 횟수를 집계하고,
정산 결과를 헬스팸 방에 올립니다. 아직 정산하지 않은 주가 여러 개면 오래된 주부터 차례로 처리합니다.

    python3 healthfam_auto.py --dry-run   # 계산만 하고 출력 (전송·기록 없음)
    python3 healthfam_auto.py --to-self   # 나와의 채팅으로 전송 (기록 없음)
    python3 healthfam_auto.py             # 헬스팸 방에 전송하고 벌금 기록 갱신

읽기: kakaocli (로컬 DB 조회) / 전송: kmsg (카카오톡 화면 자동화)
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common.config import HEALTHFAM_MEMBERS
from healthfam import (
    calculate_penalties,
    generate_penalty_summary,
    generate_workout_summary,
    update_penalty_records,
    update_total_penalty,
    TOTAL_PENALTY_FILE,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "last_settled_week.txt")  # 마지막으로 정산한 주의 월요일 (YYYY-MM-DD)
LOG_FILE = os.path.join(BASE_DIR, "auto_settle.log")

KAKAOCLI = os.path.expanduser("~/.local/bin/kakaocli")
KMSG = os.path.expanduser("~/.local/bin/kmsg-safe")  # 여러 줄 메시지를 쪼개 보내지 않도록 고친 kmsg

DB_CHAT_ID = 375704568186036  # 헬스팸 방 (카카오톡 DB의 chatId)
KMSG_ROOM = "chat_8d04051528a9"  # 헬스팸 방 (kmsg chat_id)
KMSG_SELF = "chat_b34bc169f9ec"  # 나와의 채팅 (kmsg chat_id)

TEXT_TYPES = (1, 26)  # 일반 메시지, 답장
COUNT_PATTERN = re.compile(r"\s*(\d+)\s*/\s*3")


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def query(sql):
    result = subprocess.run([KAKAOCLI, "query", sql], capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"kakaocli 조회 실패: {result.stderr.strip()[:300]}")
    return json.loads(result.stdout)


def monday_of(day):
    return day - datetime.timedelta(days=day.weekday())


def pending_weeks(today):
    """아직 정산하지 않은, 이미 끝난 주들의 월요일 목록."""
    with open(STATE_FILE, encoding="utf-8") as f:
        last = datetime.date.fromisoformat(f.read().strip())
    weeks = []
    week = last + datetime.timedelta(days=7)
    while week + datetime.timedelta(days=7) <= today:
        weeks.append(week)
        week += datetime.timedelta(days=7)
    return weeks


def check_db_complete(week_start_ts):
    """해당 주 시작부터 지금까지 방의 메시지가 DB에 빠짐없이 있는지 확인."""
    rows = query(
        f"SELECT logId, prevId FROM NTChatMessage WHERE chatId={DB_CHAT_ID} "
        f"AND sentAt>={week_start_ts - 14 * 86400} ORDER BY logId"
    )
    if not rows:
        return "해당 기간 메시지가 DB에 하나도 없음"
    ids = {r[0] for r in rows}
    breaks = [r for r in rows if r[1] not in ids]
    if len(breaks) > 1:  # 가장 오래된 메시지 하나만 앞이 끊겨 있어야 정상
        return f"메시지 연결이 {len(breaks) - 1}군데 끊겨 있음 (동기화 안 된 구간)"
    room = query(f"SELECT lastLogId FROM NTChatRoom WHERE chatId={DB_CHAT_ID}")
    if room and room[0][0] != rows[-1][0]:
        return "방의 최신 메시지가 아직 DB에 없음"
    return None


def count_week(week):
    """한 주(월 00:00 ~ 다음 월 00:00)의 멤버별 운동 횟수. 멤버가 마지막으로 올린 N/3의 N."""
    start = int(datetime.datetime.combine(week, datetime.time()).timestamp())
    end = int(datetime.datetime.combine(week + datetime.timedelta(days=7), datetime.time()).timestamp())
    rows = query(
        "SELECT COALESCE(NULLIF(u.nickName,''), u.friendNickName, ''), m.message "
        "FROM NTChatMessage m LEFT JOIN NTUser u ON u.userId=m.authorId AND u.linkId=0 "
        f"WHERE m.chatId={DB_CHAT_ID} AND m.sentAt>={start} AND m.sentAt<{end} "
        f"AND m.type IN ({','.join(map(str, TEXT_TYPES))}) ORDER BY m.sentAt, m.logId"
    )
    counts = {member: 0 for member in HEALTHFAM_MEMBERS}
    for name, message in rows:
        match = COUNT_PATTERN.match(message or "")
        if match and name in counts:
            counts[name] = int(match.group(1))
    return counts, len(rows)


def build_message(counts, total_penalty):
    penalties = calculate_penalties(counts)
    lines = generate_workout_summary(counts)
    lines.append("")
    lines.append(generate_penalty_summary(penalties, HEALTHFAM_MEMBERS))
    lines.append(f"총금액: {total_penalty + sum(penalties.values()):,}원")
    return "\n".join(lines), penalties


def read_total():
    if not os.path.exists(TOTAL_PENALTY_FILE):
        return 0
    with open(TOTAL_PENALTY_FILE, encoding="utf-8") as f:
        content = f.read().strip()
    return int(content) if content else 0


def send(chat_id, text):
    result = subprocess.run([KMSG, "send", "--chat-id", chat_id, text], capture_output=True, text=True, timeout=120)
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0 or "Message sent" not in output:
        raise RuntimeError(f"kmsg 전송 실패: {output[-300:]}")


def already_posted(text, week):
    """같은 정산 메시지가 그 주가 끝난 뒤 방에 이미 올라와 있는지 (전송은 됐는데 실패로 보고된 경우 대비)."""
    week_end = int(datetime.datetime.combine(week + datetime.timedelta(days=7), datetime.time()).timestamp())
    rows = query(
        f"SELECT message FROM NTChatMessage WHERE chatId={DB_CHAT_ID} AND sentAt>={week_end} "
        "AND message LIKE '%총금액%'"
    )
    return any((row[0] or "").strip() == text.strip() for row in rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="계산 결과만 출력")
    parser.add_argument("--to-self", action="store_true", help="나와의 채팅으로 전송하고 기록은 갱신하지 않음")
    args = parser.parse_args()

    weeks = pending_weeks(datetime.date.today())
    if not weeks:
        return

    week_ts = int(datetime.datetime.combine(weeks[0], datetime.time()).timestamp())
    problem = check_db_complete(week_ts)
    if problem and not args.dry_run:
        # 방을 한 번 열어 카카오톡이 밀린 메시지를 받아오게 한 뒤 다시 확인
        subprocess.run([KMSG, "read", "--chat-id", KMSG_ROOM, "--limit", "5"], capture_output=True, timeout=120)
        time.sleep(10)
        problem = check_db_complete(week_ts)
    if problem:
        log(f"중단: {problem}. 다음 실행 때 다시 시도합니다.")
        sys.exit(1)

    total = read_total()
    for week in weeks:
        counts, message_count = count_week(week)
        text, penalties = build_message(counts, total)
        label = f"{week:%m.%d}~{week + datetime.timedelta(days=6):%m.%d} 주차"
        if args.dry_run:
            print(f"--- {label} (메시지 {message_count}개) ---\n{text}\n")
            total += sum(penalties.values())
            continue
        if args.to_self:
            send(KMSG_SELF, f"[테스트] {label}\n{text}")
            log(f"{label} 나와의 채팅으로 테스트 전송")
            total += sum(penalties.values())
            continue
        if already_posted(text, week):
            log(f"{label} 정산 메시지가 이미 방에 있어 전송은 건너뜀")
        else:
            send(KMSG_ROOM, text)
        update_penalty_records(penalties)
        total = update_total_penalty(penalties)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(week.isoformat() + "\n")
        log(f"{label} 정산 전송 완료 (총금액 {total:,}원)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 실패 시 기록만 남기고 다음 실행에서 재시도
        log(f"오류: {e}")
        sys.exit(1)
