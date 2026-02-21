import re
import os
import shutil
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side

# =============================
# 경로 설정
# =============================
excel_path = './../KorA_Valley/KorA_Valley_tracking_2026_02_15_DB.xlsx'
output_path = './../KorA_Valley/KorA_Valley_tracking_2026_02_22_DB.xlsx'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BASE_DIR, "tracking.txt")
ARCHIVE_DIR = os.path.join(BASE_DIR, "plan_archive")

# =============================
# 이름 매핑 (⭐ value 기준 통일 ⭐)
# =============================
name_to_sheet = {
    "천승범": "천승범",
    "비씩 20 조예찬형": "조예찬",
    "신재욱": "신재욱",
    "서희찬": "서희찬",
    "윤상민": "윤상민",
    "최서연": "최서연",
    "이연희 Kirsten": "이연희",
    "김영준": "김영준",
    "정성민": "정성민",
    "김진호": "김진호",
    "유재호님": "유재호",
    "황서호형": "황서호",
    "박상준님": "박상준",
    "홍석채님": "홍석채",
    "전상우님": "전상우",
    "김세현님": "김세현",
    "비씩 20 배경덕": "배경덕"
}

RAW_NAMES = list(name_to_sheet.keys())
SHEET_NAMES = list(name_to_sheet.values())

# =============================
# 엑셀 로드
# =============================
wb = load_workbook(excel_path)
db_sheet = wb["DB"]
plan_sheet = wb["계획"]

person_sheets = {
    name: wb[name]
    for name in SHEET_NAMES
    if name in wb.sheetnames
}

# =============================
# 스타일
# =============================
RED_CENTER = Font(color="FFFF0000")
CENTER = Alignment(horizontal="center")
RIGHT = Alignment(horizontal="right")

THIN_BORDER = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

# =============================
# 날짜 기록 함수
# =============================
def write_db_date(sheet, r, c, dt):
    sheet.cell(r, c, dt).number_format = "yyyy.mm.dd"

def write_plan_date(sheet, r, c, dt):
    cell = sheet.cell(r, c, dt)
    cell.number_format = 'm"월" d"일"'
    cell.font = RED_CENTER
    cell.alignment = CENTER

# =============================
# DB row 찾기
# =============================
def find_db_row(name, plan_no):
    for r in range(2, db_sheet.max_row + 1):
        if db_sheet.cell(r,2).value == name and db_sheet.cell(r,3).value == plan_no:
            return r
    return None

# =============================
# tracking.txt 백업
# =============================
date_match = re.search(r'(\d{4}_\d{2}_\d{2})', output_path)
if not date_match:
    raise ValueError("output_path에서 날짜 추출 실패")

os.makedirs(ARCHIVE_DIR, exist_ok=True)
archive_path = os.path.join(ARCHIVE_DIR, f"archive_{date_match.group(1)}.txt")
shutil.copy(TRACKING_FILE, archive_path)
print(f"📦 archive 저장 완료 → {archive_path}")

# =============================
# TXT 파싱
# =============================
with open(TRACKING_FILE, encoding="utf-8") as f:
    lines = f.read().splitlines()

current_date = None

for line in lines:
    line = re.sub(r'\s+', ' ', line.strip())
    if not line:
        continue

    # 날짜
    m = re.match(r'(\d{4}년 \d{1,2}월 \d{1,2}일)', line)
    if m:
        current_date = datetime.strptime(m.group(1), "%Y년 %m월 %d일")
        continue

    # 시간 제거
    line = re.sub(r'^(오전|오후) \d{1,2}:\d{2} ', '', line)

    raw_name, name, content = None, None, None
    for candidate in RAW_NAMES:
        if line.startswith(candidate + ' '):
            raw_name = candidate
            name = name_to_sheet[candidate]
            content = line[len(candidate)+1:].strip()
            break

    if not name:
        continue

    # -------------------------
    # 계획 작성
    # -------------------------
    plan_match = re.search(r'(\d+)\s*번[째쨰]?\s*(계획|게획|목표)\s*:?\s*(.*)', content)
    if plan_match and '✅' not in content:
        plan_no = int(plan_match.group(1))
        plan_text = plan_match.group(3).strip()

        if not find_db_row(name, plan_no):
            r = db_sheet.max_row + 1
            db_sheet.append([r-1, name, plan_no, plan_text, "미완료", None, None])
            write_db_date(db_sheet, r, 6, current_date)

        # 계획 시트 날짜
        col = SHEET_NAMES.index(name) + 3
        row = plan_no + 2
        if not plan_sheet.cell(row, col).value:
            write_plan_date(plan_sheet, row, col, current_date)

        # 개인 시트 계획 내용
        if name in person_sheets:
            person_sheets[name].cell(row, 3, plan_text)

    # -------------------------
    # 완료 처리
    # -------------------------
    if '✅' in content:
        m = re.search(r'(\d+)\s*번', content)
        if not m:
            continue

        plan_no = int(m.group(1))
        r = find_db_row(name, plan_no)
        if r:
            db_sheet.cell(r,5,"완료")
            write_db_date(db_sheet, r, 7, current_date)

        col = SHEET_NAMES.index(name) + 3
        row = plan_no + 2
        plan_sheet.cell(row, col, "O").font = RED_CENTER
        plan_sheet.cell(row, col).alignment = CENTER

        if name in person_sheets:
            c = person_sheets[name].cell(row,3)
            if c.value:
                c.font = Font(strike=True)

# =============================
# 계획 시트 번호 확장 (B열만)
# =============================
max_plan_no = max(
    [db_sheet.cell(r,3).value for r in range(2, db_sheet.max_row+1)
     if isinstance(db_sheet.cell(r,3).value, int)],
    default=0
)

for n in range(1, max_plan_no + 1):
    r = n + 2
    b = plan_sheet.cell(r,2,n)
    b.alignment = RIGHT
    b.border = THIN_BORDER

# =============================
# 각자 시트 번호 확장 (개인별)
# =============================
for sheet in person_sheets.values():
    last_row = max(
        [r for r in range(3, sheet.max_row+1) if sheet.cell(r,3).value],
        default=2
    )
    max_no = last_row - 2
    for n in range(1, max_no + 1):
        r = n + 2
        b = sheet.cell(r,2,n)
        b.alignment = RIGHT
        b.border = THIN_BORDER

# =============================
# 저장
# =============================
wb.save(output_path)
print("✅ 전체 시트(DB + 계획 + 개인 시트) 업데이트 완료")