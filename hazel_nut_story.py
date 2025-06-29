from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import re
from collections import defaultdict

# 1. 이미지 불러오기
template_path = "./Planner.png"  # ← 너의 파일 경로로 수정
image = Image.open(template_path).convert("RGB")
draw = ImageDraw.Draw(image)

# 2. 텍스트 입력
text_input = """
2025년 6월 18일 수요일
오후 1:00 천승범 언어 공부 2200 2220
"""

# 📆 날짜 추출 및 표시
lines = text_input.strip().splitlines()
date_kr = lines[0]
match = re.search(r"(\d{4})년 (\d{1,2})월 (\d{1,2})일", date_kr)
if match:
    year, month, day = match.groups()
    date_obj = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
    date_text = date_obj.strftime("%a %m.%d.")
else:
    date_text = "Unknown"

# 🖋 Font 설정
font_path = "/Users/cheonseungbeom/Desktop/CSB/그 외/BinggraeSamanco-Bold.otf"
date_font = ImageFont.truetype(font_path, size=54)
plan_font = ImageFont.truetype(font_path, size=40)

draw.text((160, 150), date_text, font=date_font, fill="black")

# ✅ 시간 파싱 함수 수정
def parse_time(time_str):
    """610 -> (6, 10), 720 -> (7, 20), 1040 -> (10, 40) 형태로 변환"""
    time_num = int(time_str)
    
    if time_num < 100:  # 예: 90 -> 0시 90분 (잘못된 입력)
        hour = 0
        minute = time_num
    elif time_num < 1000:  # 3자리: 610 -> 6시 10분
        hour = time_num // 100
        minute = time_num % 100
    else:  # 4자리: 1040 -> 10시 40분
        hour = time_num // 100
        minute = time_num % 100
    
    return hour, minute

def time_to_minutes(hour, minute):
    """시간을 분으로 변환 (6시 = 360분)"""
    return hour * 60 + minute

# ✅ 우선순위 설정 (수동으로 지정)
priority_order = [
    "물전 중간",
    "중문이 중간",
    "고문상 중간",
    "컴구 기말",
    "데구 기말",
    "물전 기말",
    "고문상 기말",
    "중문이 기말",
    "고문상 퀴즈",
    "컴구 수업",
    "데구 수업",
    "데구 강의",
    "고문상 토론",
    "전전101 조교",
    "컴구 과제",
    "중문이 과제",
    "컴구 공부",
    "데구 공부",
    "물전 공부",
    "중문이 공부",
    "고문상 공부",
    "전전101 채점",
    "독서",
    "헬스",
    "언어 공부",
    "유익한 영상",
    "CS 공부",
    "BD Assignment",
    "JP Assignment",
    "Apple Assignment",
    "GTC Assignment",
    "GTC Work",
    "개발블로그 작성",
    "글쓰기",
    "기록/정산 자동화",
    "플래너 제작",
    "친구글 읽기",
    "글 읽기",
    "LinkedIn 수정",
    "코라밸리 운영",
    "코라밸리/헬스팸 운영",
    "플래너 작성",
    "Txx 사전과제",
    "BD Meeting",
    "GQ Meeting",
    "코라밸리 커피챗",
    "토크",
    "GTC 이메일 전송",
]

def get_plan_priority(plan_name):
    """계획명의 우선순위를 반환 (낮을수록 높은 우선순위)"""
    for i, priority_plan in enumerate(priority_order):
        if priority_plan == plan_name:
            return i + 1
    return 999  # 우선순위에 없는 계획은 맨 뒤로

# ✅ 계획 추출
plan_lines = lines[1:]
plan_dict = defaultdict(list)
for line in plan_lines:
    parts = line.strip().split()
    if len(parts) >= 5:
        plan_text = " ".join(parts[3:-2])
        # 시간 파싱 수정
        start_time_str = parts[-2]
        end_time_str = parts[-1]
        
        start_hour, start_min = parse_time(start_time_str)
        end_hour, end_min = parse_time(end_time_str)
        
        start_total_min = time_to_minutes(start_hour, start_min)
        end_total_min = time_to_minutes(end_hour, end_min)
        
        plan_dict[plan_text].append((start_total_min, end_total_min))
        
unique_plans = list(plan_dict.keys())
unique_plans.sort(key=get_plan_priority)
print("우선순위 순서:")
for i, plan in enumerate(unique_plans):
    priority = get_plan_priority(plan)
    print(f"{i+1}. {plan} (우선순위: {priority})")
unique_plans += [""] * (12 - len(unique_plans))  # 항상 12개

# ✅ 체크리스트 렌더링
start_x = 230
start_y = 285
line_spacing = 70
checkbox_x = 162

checkbox_checked = Image.open("./checked.png").convert("RGBA").resize((42, 42))
checkbox_unchecked = Image.open("./unchecked.png").convert("RGBA").resize((42, 42))

for i, plan in enumerate(unique_plans):
    y = start_y + i * line_spacing
    checkbox = checkbox_checked if plan else checkbox_unchecked
    checkbox_y = y + (plan_font.size // 2) - 20  # center align
    image.paste(checkbox, (checkbox_x, int(checkbox_y)), mask=checkbox)
    if plan:
        draw.text((start_x, y), plan, font=plan_font, fill="black")

# ✅ 시간표 위치 및 설정
# 오른쪽 시간표 (06:00 ~ 24:00)
right_timeline_x = 558
right_timeline_y_start = 243
# 왼쪽 시간표 (00:00 ~ 06:00)  
left_timeline_x = 133
left_timeline_y_start = 1166

timeline_width = 394
hour_height = 77
bar_height = 60
cell_width = timeline_width // 6  # 10분 = 1칸 (1시간당 6칸)

colors = ["#FA7D7C", "#F9AE7D", "#F7FC7F", "#7DF97E", "#80E0FA",
          "#7D7DFA", "#CA7CFA", "#CD7D7E", "#C5967B", "#CDCD7D",
          "#7FCD7F", "#80BDCD"]

# ✅ 반원형 블럭 그리기 함수
def draw_rounded_block(x1, y1, x2, y2, color):
    radius = (y2 - y1) / 2
    draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=color)
    draw.pieslice((x1, y1, x1 + 2 * radius, y2), 90, 270, fill=color)
    draw.pieslice((x2 - 2 * radius, y1, x2, y2), 270, 90, fill=color)

# 8. 계획 막대 그리기 (줄마다 정확한 시작 칸과 길이 계산)
for i, (plan_name, time_ranges) in enumerate(plan_dict.items()):
    plan_priority_index = next(j for j, p in enumerate(unique_plans) if p == plan_name)
    color = colors[plan_priority_index % len(colors)]
    print(f"계획: {plan_name} → 색깔 인덱스: {plan_priority_index} → 색깔: {color}")
    for start_total_min, end_total_min in time_ranges:
        current_min = start_total_min
        print(f"  시간대: {current_min//60}:{current_min%60:02d} ~ {end_total_min//60}:{end_total_min%60:02d}")
        
        while current_min < end_total_min:
            current_hour = current_min // 60
            current_minute_in_hour = current_min % 60
            
            # 현재 시간의 다음 정시까지의 분
            next_hour_min = (current_hour + 1) * 60
            
            # 이번 시간대에서 끝나는 시점 계산
            segment_end_min = min(end_total_min, next_hour_min)
            
            # 현재 시간대에서의 시작/끝 칸 계산 (10분 단위)
            start_cell = current_minute_in_hour // 10  # 0~5
            end_minute_in_hour = segment_end_min % 60
            if end_minute_in_hour == 0 and segment_end_min > current_min:
                end_cell = 6  # 정시인 경우
            else:
                end_cell = (end_minute_in_hour + 9) // 10  # 올림 처리
            
            # 막대 그리기
            if end_cell > start_cell:
                x1_offset = start_cell * cell_width
                x2_offset = end_cell * cell_width
                
                # 시간대에 따라 왼쪽/오른쪽 시간표 선택
                if 0 <= current_hour < 6:  # 00:00 ~ 05:59 → 왼쪽 시간표
                    timeline_x = left_timeline_x
                    timeline_y_start = left_timeline_y_start
                    y = timeline_y_start + current_hour * hour_height + (hour_height - bar_height) / 2
                    print(f"    {current_hour}시: {start_cell}칸~{end_cell}칸 (길이: {end_cell-start_cell}칸) [왼쪽]")
                elif 6 <= current_hour < 24:  # 06:00 ~ 23:59 → 오른쪽 시간표
                    timeline_x = right_timeline_x
                    timeline_y_start = right_timeline_y_start
                    y = timeline_y_start + (current_hour - 6) * hour_height + (hour_height - bar_height) / 2
                    print(f"    {current_hour}시: {start_cell}칸~{end_cell}칸 (길이: {end_cell-start_cell}칸) [오른쪽]")
                else:
                    current_min = segment_end_min
                    continue
                
                x1 = timeline_x + x1_offset
                x2 = timeline_x + x2_offset
                draw_rounded_block(x1, y, x2, y + bar_height, color)
            
            current_min = segment_end_min

# 💾 저장 (월별 폴더에 날짜별 파일명으로)
import os

# 날짜에서 연-월 추출
if match:
    year, month, day = match.groups()
    # 폴더 경로 생성
    folder_path = f"remade_schedule/{year}-{month.zfill(2)}"
    os.makedirs(folder_path, exist_ok=True)
    
    # 파일명 생성
    filename = f"story-{year}-{month.zfill(2)}-{day.zfill(2)}.jpeg"
    output_path = os.path.join(folder_path, filename)
else:
    # 날짜 파싱 실패시 기본 경로
    output_path = "./planner_with_date.jpeg"

image.save(output_path)
print(f"✅ 플래너 저장 완료: {output_path}")