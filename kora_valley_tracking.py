import re
from openpyxl import load_workbook
from openpyxl.styles import Font
from datetime import datetime
from openpyxl.styles import Alignment

# 파일 경로
excel_path = './../KorA_Valley/KorA_Valley_tracking.xlsx'  # 수정
output_path = './../KorA_Valley/KorA_Valley_tracking.xlsx'

# 사람 이름 목록
names = ["천승범", "조예찬 John", "최재훈", "송의현", "이승준", "양수민", "신재욱", "이승헌", "진세", "서희찬", "신영진", "윤상민"]

# 사람 이름과 시트 이름 매핑 (직접 설정)
name_to_sheet = {
    "천승범": "천승범",
    "조예찬 John": "조예찬",
    "최재훈": "최재훈",
    "송의현": "송의현",
    "이승준": "이승준",
    "양수민": "양수민",
    "신재욱": "신재욱",
    "이승헌": "이승헌",
    "진세": "김진세",  # '진세'는 '김진세' 시트에 기록
    "서희찬": "서희찬",
    "신영진": "신영진",
    "윤상민": "윤상민"
}

# 엑셀 파일 읽기
wb = load_workbook(excel_path)

# '계획' 시트 찾기
if '계획' in wb.sheetnames:
    plan_sheet = wb['계획']
else:
    print("'계획' 시트를 찾을 수 없습니다. 첫 번째 시트를 사용합니다.")
    plan_sheet = wb.active

# 각 사람별 시트 찾기 및 매핑
name_sheets = {}
for name, sheet_name in name_to_sheet.items():
    if sheet_name in wb.sheetnames:
        name_sheets[name] = wb[sheet_name]
    else:
        print(f"'{sheet_name}' 시트를 찾을 수 없습니다. 해당 사람의 계획 내용은 기록되지 않습니다: {name}")

# 입력 텍스트 읽기
with open('tracking.txt', 'r', encoding='utf-8') as f:
    tracking_list = f.read()

current_date = None
lines = tracking_list.strip().split('\n')

for line in lines:
    line = re.sub(r'\s+', ' ', line.strip())  # 공백 여러개 정리
    if not line:
        continue

    # 날짜 줄
    date_match = re.match(r'(\d{4}년 \d{1,2}월 \d{1,2}일)', line)
    if date_match:
        date_obj = datetime.strptime(date_match.group(1), "%Y년 %m월 %d일")
        current_date = f"{date_obj.month}월 {date_obj.day}일"
        continue
    
    # 이름 자동 매칭
    name = None
    content = None

    # 여기서 시간(오전/오후 시간) 제거
    line = re.sub(r'^(오전|오후) \d{1,2}:\d{2} ', '', line)

    for candidate in names:
        if line.startswith(candidate + ' '):  # 이름 뒤에 공백 확인
            name = candidate
            content = line[len(candidate)+1:].strip()  # 이름+공백만큼 잘라서 content 추출
            break

    if not name or not content:
        continue  # 이름 못 찾았으면 건너뜀

    name_idx = names.index(name)
    col = name_idx + 3  # 열 인덱스 (3열부터 시작)

    # 계획 패턴 확인 - "번째 계획:" 형식만 처리
    plan_match = re.search(r'(\d+)번[째쨰]?\s*계획\s*:?\s*(.*)', content)
    if plan_match and '✅' not in content:  # 완료 표시가 없는 경우만 계획으로 처리
        plan_number = int(plan_match.group(1))
        plan_content = plan_match.group(2).strip()
        row = plan_number + 2  # 행 인덱스 (3행부터 시작)
        
        # '계획' 시트에 날짜 기록
        if not plan_sheet.cell(row=row, column=col).value:
            cell = plan_sheet.cell(row=row, column=col, value=current_date)
            cell.font = Font(color="FFFF0000")
            cell.alignment = Alignment(horizontal="center")
            cell.number_format = '@'
        
        # 해당 이름의 시트가 있다면 계획 내용 기록 - 3번째 열에 기록
        if name in name_sheets and plan_content:  # 계획 내용이 있는 경우에만 기록
            cell = name_sheets[name].cell(row=row, column=3, value=plan_content)  # 3번째 열로 수정
            # 계획 페이지를 제외한 다른 페이지는 빨간색 글씨 사용 안 함
            cell.alignment = Alignment(horizontal="left")

    # 완료 처리
    if '✅' in content:
        completion_match = re.search(r'✅\s*(\d+)번[째쨰]?\s*계획\s*완료', content)
        if completion_match:
            plan_number = int(completion_match.group(1))
            row = plan_number + 2
            
            # '계획' 시트에 완료 표시
            cell = plan_sheet.cell(row=row, column=col, value='O')
            cell.font = Font(color="FFFF0000")
            cell.alignment = Alignment(horizontal="center")

# 저장
wb.save(output_path)
print(f"✅ 완료! 저장된 엑셀 파일: {output_path}")