# ✅ 필요한 라이브러리 import
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import re
from collections import defaultdict
import os

# ✅ 기본 설정
TEMPLATE_PATH = "hazel_nut_story/input_img/Planner.png"
FONT_PATH = "/Users/cheonseungbeom/Desktop/CSB/그 외/BinggraeSamanco-Bold.otf"
CHECKED_PATH = "hazel_nut_story/input_img/checked.png"
UNCHECKED_PATH = "hazel_nut_story/input_img/unchecked.png"
OUTPUT_DIR = "hazel_nut_story/remade_schedule"

# ✅ 시간 파싱 함수
def parse_time(time_str):
    time_num = int(time_str)
    if time_num < 100:
        return 0, time_num
    elif time_num < 1000:
        return time_num // 100, time_num % 100
    else:
        return time_num // 100, time_num % 100

def time_to_minutes(hour, minute):
    return hour * 60 + minute

# ✅ 우선순위 리스트
priority_order = [
    "물전 중간", "중문이 중간", "고문상 중간", "컴구 기말", "데구 기말",
    "물전 기말", "고문상 기말", "중문이 기말", "고문상 퀴즈", "컴구 수업",
    "데구 수업", "데구 강의", "고문상 토론", "전전101 조교", "컴구 과제",
    "중문이 과제", "컴구 공부", "데구 공부", "물전 공부", "중문이 공부",
    "고문상 공부", "전전101 채점", "독서", "헬스", "언어 공부", "유익한 영상",
    "CS 공부", "코테 공부", "BD Assignment", "JP Assignment", "Apple Assignment",
    "GTC Assignment", "GTC Work", "개발블로그 작성", "글쓰기", "기록/정산 자동화",
    "플래너 제작", "친구글 읽기", "글 읽기", "LinkedIn 수정", "코라밸리 운영",
    "코라밸리/헬스팸 운영", "플래너 작성", "Txx 사전과제", "BD Meeting",
    "GQ Meeting", "Apple Meeting", "코라밸리 커피챗", "커피챗", "토크",
    "GTC 이메일 전송",
]

def get_plan_priority(plan_name):
    for i, name in enumerate(priority_order):
        if plan_name == name:
            return i + 1
    return 999

# ✅ 메인 생성 함수
def generate_daily_planners(text_input):
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
        date_font = ImageFont.truetype(FONT_PATH, size=54)
        plan_font = ImageFont.truetype(FONT_PATH, size=40)

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
                draw.text((start_x, y), plan, font=plan_font, fill="black")

        # 시간표 막대
        colors = ["#FA7D7C", "#F9AE7D", "#F7FC7F", "#7DF97E", "#80E0FA",
                  "#7D7DFA", "#CA7CFA", "#CD7D7E", "#C5967B", "#CDCD7D",
                  "#7FCD7F", "#80BDCD"]

        def draw_rounded_block(x1, y1, x2, y2, color):
            r = (y2 - y1) / 2
            draw.rectangle((x1 + r, y1, x2 - r, y2), fill=color)
            draw.pieslice((x1, y1, x1 + 2 * r, y2), 90, 270, fill=color)
            draw.pieslice((x2 - 2 * r, y1, x2, y2), 270, 90, fill=color)

        hour_h, bar_h, width = 77, 60, 394
        cwidth = width // 6
        r_x, r_y, l_x, l_y = 558, 243, 133, 1166

        for i, (plan_name, ranges) in enumerate(plan_dict.items()):
            pidx = next(j for j, p in enumerate(unique_plans) if p == plan_name)
            color = colors[pidx % len(colors)]
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
                            draw_rounded_block(l_x + x1, y, l_x + x2, y + bar_h, color)
                        elif 6 <= ch < 24:
                            y = r_y + (ch - 6) * hour_h + (hour_h - bar_h) / 2
                            draw_rounded_block(r_x + x1, y, r_x + x2, y + bar_h, color)
                    s = seg_end

        # 저장
        folder_path = f"{OUTPUT_DIR}/{year}-{month.zfill(2)}"
        os.makedirs(folder_path, exist_ok=True)
        output_path = os.path.join(folder_path, f"story-{year}-{month.zfill(2)}-{day.zfill(2)}.jpeg")
        image.save(output_path)
        print(f"✅ {output_path} 저장 완료")


# ✅ 테스트 입력 실행 예시
if __name__ == "__main__":
    with open("hazel_nut_story/schedule_input.txt", "r", encoding="utf-8") as f:
        text = f.read()
    generate_daily_planners(text)