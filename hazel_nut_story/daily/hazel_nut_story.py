"""
일일 플래너 이미지 자동 생성

schedule_input.txt 텍스트를 파싱하여 날짜별 플래너 이미지를 생성합니다.
- 체크리스트 (우선순위 정렬)
- 색상 코딩된 시간표 막대 (0~24시)
"""

import os
import re
import sys
from collections import defaultdict
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from common.config import FONT_SAMANCO, COLOR_12
from common.time_utils import parse_time, time_to_minutes

# =============================
# 경로 설정
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "input_img", "Planner.png")
CHECKED_PATH = os.path.join(BASE_DIR, "input_img", "checked.png")
UNCHECKED_PATH = os.path.join(BASE_DIR, "input_img", "unchecked.png")
OUTPUT_DIR = os.path.join(BASE_DIR, "remade_schedule")
SCHEDULE_INPUT = os.path.join(BASE_DIR, "schedule_input.txt")

# =============================
# 우선순위 리스트
# =============================
PRIORITY_ORDER = [
    "코테 시험", "게임QA 일", "물전 중간", "중문이 중간", "고문상 중간", "컴구 기말", "데구 기말",
    "물전 기말", "고문상 기말", "중문이 기말", "고문상 퀴즈", "바전공 수업", "딥실 수업", "컴구 수업",
    "데구 수업", "계량경제학 수업", "주채파 수업", "데구 강의", "바전공 강의", "고문상 토론", "전전101 조교", "컴구 과제",
    "중문이 과제", "바전공 과제", "딥실 예렢 작성", "딥실 결렢 작성", "컴구 공부", "데구 공부", "물전 공부", "중문이 공부",
    "고문상 공부", "전전101 채점", "독서", "헬스", "언어 공부", "유익한 영상",
    "CS 공부", "운영체제론 공부", "계량경제학 공부", "주채파 공부", "대규모시스템 공부", "기술블로그 읽기", "코딩 공부", "코테 공부",
    "프로젝트 복습", "프로젝트 정리", "기술면접 공부", "Spring 공부", "SpringBoot 공부", "JPA 공부", "리액티브 공부",
    "Redis 공부", "Kafka 공부", "Django 공부", "Nginx 공부", "PostgreSQL 공부", "MySQL 공부", "Docker 공부",
    "AWS 공부", "테크 공부", "GDGoC T19 발표준비", "SURI 공부", "SURI 과제", "퀀트 공부",
    "논문 리딩", "논문 분석", "BOTA 질문답변",
    "BD Assignment", "JP Assignment", "Apple Assignment",
    "GTC Assignment", "GTC 일", "ZERO to AI 일", "이력서 수정", "포트폴리오 수정", "TOEIC 공부",
    "개발블로그 작성", "글쓰기", "기록/정산 자동화",
    "플래너 제작", "코딩 작업", "독후감 작성", "친구글 읽기", "글 읽기", "LinkedIn 수정",
    "코라밸리 일", "코라밸리 웹개발", "퐅폴 제작", "코라밸리 운영",
    "코라밸리/헬스팸 운영", "지원서 작성", "플래너 작성", "T사 사전과제", "오픽 공부",
    "주식스터디 준비", "주식스터디 과제", "주식 공부", "인스타 제작", "커피챗 내용정리",
    "사이드프로젝트 개발",
    "GDGoC T19 세션", "GDGoC 세션", "SURI 세션",
    "BD Meeting", "GQ Meeting", "Apple Meeting", "GTC Meeting",
    "FBA Quant FE세션", "FBA Quant AP세션", "BOTA 미팅",
    "ZERO to AI 미팅", "코라밸리 미팅", "주식스터디", "코라밸리 커피챗", "커피챗", "독서모임", "토크",
]

_priority_index = {name: i + 1 for i, name in enumerate(PRIORITY_ORDER)}


def get_plan_priority(plan_name):
    """우선순위 인덱스 반환. 목록에 없으면 999."""
    return _priority_index.get(plan_name, 999)


def draw_rounded_block(draw, x1, y1, x2, y2, color):
    """양쪽 끝이 둥근 막대를 그립니다."""
    r = (y2 - y1) / 2
    draw.rectangle((x1 + r, y1, x2 - r, y2), fill=color)
    draw.pieslice((x1, y1, x1 + 2 * r, y2), 90, 270, fill=color)
    draw.pieslice((x2 - 2 * r, y1, x2, y2), 270, 90, fill=color)


def generate_daily_planners(text_input):
    """
    텍스트 입력을 파싱하여 날짜별 플래너 이미지를 생성합니다.

    Args:
        text_input: schedule_input.txt 형식의 텍스트
    """
    # 날짜별로 분리
    blocks = re.split(r"(?=\d{4}년 \d{1,2}월 \d{1,2}일)", text_input.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue

        # 날짜 파싱
        date_kr = lines[0]
        match = re.search(r"(\d{4})년 (\d{1,2})월 (\d{1,2})일", date_kr)
        if not match:
            continue
        year, month, day = match.groups()
        date_obj = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        date_text = date_obj.strftime("%a %m.%d.")

        # 플래너 이미지 불러오기
        image = Image.open(TEMPLATE_PATH).convert("RGB")
        draw = ImageDraw.Draw(image)
        date_font = ImageFont.truetype(FONT_SAMANCO, size=54)
        plan_font = ImageFont.truetype(FONT_SAMANCO, size=40)

        draw.text((160, 150), date_text, font=date_font, fill="black")

        # 계획 추출 및 정리
        plan_dict = defaultdict(list)
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                plan = " ".join(parts[3:-2])
                s_hour, s_min = parse_time(parts[-2])
                e_hour, e_min = parse_time(parts[-1])
                plan_dict[plan].append((time_to_minutes(s_hour, s_min), time_to_minutes(e_hour, e_min)))

        unique_plans = list(plan_dict.keys())
        unique_plans.sort(key=get_plan_priority)
        unique_plans += [""] * (12 - len(unique_plans))

        # 체크리스트
        start_x, start_y, line_spacing, checkbox_x = 230, 285, 70, 162
        checked = Image.open(CHECKED_PATH).convert("RGBA").resize((42, 42))
        unchecked = Image.open(UNCHECKED_PATH).convert("RGBA").resize((42, 42))

        for i, plan in enumerate(unique_plans):
            y = start_y + i * line_spacing
            checkbox = checked if plan else unchecked
            image.paste(checkbox, (checkbox_x, y + (plan_font.size // 2) - 20), mask=checkbox)
            if plan:
                color = COLOR_12[i % len(COLOR_12)]

                # 계획 텍스트 그리기
                draw.text((start_x, y), plan, font=plan_font, fill="black")

                # 텍스트 길이 기반 색상 표시 원
                text_width = draw.textlength(plan, font=plan_font)
                circle_x = start_x + text_width + 30
                circle_y = y + plan_font.size // 2
                draw.ellipse(
                    [circle_x - 10, circle_y - 10, circle_x + 10, circle_y + 10],
                    fill=color,
                    outline=None,
                )

        # 시간표 막대
        hour_h, bar_h, width = 77, 60, 394
        cwidth = width // 6
        r_x, r_y, l_x, l_y = 558, 243, 133, 1166

        for plan_name, ranges in plan_dict.items():
            pidx = next(j for j, p in enumerate(unique_plans) if p == plan_name)
            color = COLOR_12[pidx % len(COLOR_12)]
            for s, e in ranges:
                while s < e:
                    ch = s // 60
                    cm = s % 60
                    next_h = (ch + 1) * 60
                    seg_end = min(e, next_h)
                    sc = cm // 10
                    em = seg_end % 60
                    ec = 6 if em == 0 and seg_end > s else (em + 9) // 10
                    if ec > sc:
                        x1, x2 = sc * cwidth, ec * cwidth
                        if 0 <= ch < 6:
                            y = l_y + ch * hour_h + (hour_h - bar_h) / 2
                            draw_rounded_block(draw, l_x + x1, y, l_x + x2, y + bar_h, color)
                        elif 6 <= ch < 24:
                            y = r_y + (ch - 6) * hour_h + (hour_h - bar_h) / 2
                            draw_rounded_block(draw, r_x + x1, y, r_x + x2, y + bar_h, color)
                    s = seg_end

        # 저장
        folder_path = os.path.join(OUTPUT_DIR, f"{year}-{month.zfill(2)}")
        os.makedirs(folder_path, exist_ok=True)
        output_path = os.path.join(folder_path, f"story-{year}-{month.zfill(2)}-{day.zfill(2)}.jpeg")
        image.save(output_path)
        print(f"✅ {output_path} 저장 완료")


if __name__ == "__main__":
    with open(SCHEDULE_INPUT, "r", encoding="utf-8") as f:
        text = f.read()
    generate_daily_planners(text)