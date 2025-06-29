import os
import re

def parse_chat_log(log_text):
    """
    채팅 로그를 파싱하여 각 사람의 운동 횟수를 추출합니다.
    """
    # 채팅 로그에서 운동 횟수를 추출하기 위한 패턴
    # 1. "이름: N/3" 형식 (요약 리스트에 있는 형식)
    summary_pattern = re.compile(r'([가-힣]+): (\d+)/3')
    
    # 2. "오후/오전 시간 이름 N/3" 형식 (개별 메시지 형식)
    message_pattern = re.compile(r'(?:오[전후] \d+:\d+ )?([가-힣]+) (\d+)/3')
    
    # 각 줄을 분석하여 운동 기록을 추출
    lines = log_text.strip().split('\n')
    
    # 사람별 운동 횟수를 저장할 딕셔너리
    latest_workout_counts = {}
    
    # 로그를 분석하여 각 사람의 마지막 운동 기록을 찾습니다
    for line in lines:
        # 요약 리스트 형식 확인
        summary_matches = summary_pattern.findall(line)
        if summary_matches:
            for name, count in summary_matches:
                latest_workout_counts[name] = int(count)
        
        # 개별 메시지 형식 확인
        message_matches = message_pattern.findall(line)
        if message_matches:
            for name, count in message_matches:
                latest_workout_counts[name] = int(count)
    
    return latest_workout_counts

def calculate_penalties(workout_counts):
    """
    운동 횟수에 따라 벌금을 계산합니다.
    """
    penalties = {}
    
    for person, count in workout_counts.items():
        if count >= 3 or count == -1:  # 운동을 모두 완료했거나 예외 케이스인 경우
            penalties[person] = 0
        else:
            penalties[person] = 15000 - 5000 * count
    
    return penalties

def generate_workout_summary(workout_counts):
    """
    각 사람의 운동 상태를 요약합니다.
    """
    workout_text = []
    for person, num in sorted(workout_counts.items()):
        if num == -1:
            workout_text.append(f"{person}: 0/0")
        else:
            workout_text.append(f"{person}: {num}/3")
    
    return workout_text

def generate_penalty_summary(penalties, member_order):
    """
    벌금 정보를 그룹화하여 요약합니다.
    """
    penalty_groups = {
        5000: [],
        10000: [],
        15000: []
    }
    
    for person, fine in penalties.items():
        if fine > 0:
            penalty_groups[fine].append(person)
    
    penalty_text = []
    
    for fine in [5000, 10000, 15000]:
        if penalty_groups[fine]:
            names = sorted(penalty_groups[fine], key=lambda name: member_order.index(name))
            if len(names) > 1:
                penalty_text.append(f"{' '.join(names)} {fine}원씩")
            else:
                penalty_text.append(f"{' '.join(names)} {fine}원")
    
    if penalty_text:
        return "벌금 " + " ".join(penalty_text)
    else:
        return "벌금 없음"

def update_penalty_records(penalties):
    """
    개인별 벌금 기록을 업데이트합니다.
    """
    penalty_file = "penalty_list.txt"
    penalty_totals = {}
    
    # 파일이 존재하는지 확인
    if os.path.exists(penalty_file):
        # 현재 벌금 기록을 파일에서 읽어옵니다
        with open(penalty_file, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    person, amount = parts
                    penalty_totals[person] = int(amount.replace(',', '').replace('원', ''))
    
    # 개인별 벌금 기록 업데이트
    for person, fine in penalties.items():
        if fine > 0:
            if person in penalty_totals:
                penalty_totals[person] += fine
            else:
                penalty_totals[person] = fine
    
    # 업데이트된 기록을 파일에 저장
    with open(penalty_file, "w", encoding="utf-8") as file:
        for person, total_fine in sorted(penalty_totals.items()):
            formatted_fine = f"{total_fine:,}원"
            file.write(f"{person}: {formatted_fine}\n")
    
    return penalty_totals

def update_total_penalty(penalties):
    """
    총 벌금 금액을 업데이트합니다.
    """
    total_penalty_file = "total_penalty.txt"
    
    # 파일이 존재하는지 확인
    if os.path.exists(total_penalty_file):
        # 현재 총 벌금을 파일에서 읽어옵니다
        with open(total_penalty_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
            total_penalty = int(content) if content else 0
    else:
        # 파일이 없으면 초기화
        total_penalty = 0
    
    # 이번 라운드의 벌금 합계 계산
    current_total_penalty = sum(penalties.values())
    
    # 기존 총액에 추가
    total_penalty += current_total_penalty
    
    # 업데이트된 총액을 파일에 저장
    with open(total_penalty_file, "w", encoding="utf-8") as file:
        file.write(str(total_penalty))
    
    return total_penalty

def main():
    """
    메인 함수 - health_log.txt 파일에서 채팅 로그를 읽어오고 결과를 출력합니다.
    """
    print("운동 추적 및 벌금 계산 프로그램을 시작합니다.")
    
    # health_log.txt 파일에서 채팅 로그 읽어오기
    try:
        with open("health_log.txt", "r", encoding="utf-8") as file:
            chat_log = file.read()
        print("health_log.txt 파일을 성공적으로 불러왔습니다.")
    except FileNotFoundError:
        print("Error: health_log.txt 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"Error: 파일을 읽는 중 오류가 발생했습니다: {e}")
        return
    
    # 채팅 로그에서 운동 횟수 추출
    workout_counts = parse_chat_log(chat_log)
    
    # 기본 멤버 목록 (운동 기록이 없는 경우 기본값 0으로 설정)
    default_members = [
        '권정호',
        '성현우',
        '신동훈',
        '이명건', 
        '이승준',
        '이형민',
        '전은결',
        '천승범',
        '황동근'
    ]
    
    for member in default_members:
        if member not in workout_counts:
            workout_counts[member] = 0
            
    # workout_counts에서 default_members만 남기기
    workout_counts = {name: count for name, count in workout_counts.items() if name in default_members}
    
    # 벌금 계산
    penalties = calculate_penalties(workout_counts)
    
    # 운동 요약 생성 및 출력
    workout_summary = generate_workout_summary(workout_counts)
    for line in workout_summary:
        print(line)
    print()
    
    # 벌금 요약 생성 및 출력
    penalty_summary = generate_penalty_summary(penalties, default_members)
    print(penalty_summary)
    
    # 개인별 벌금 기록 업데이트
    update_penalty_records(penalties)
    
    # 총 벌금 업데이트 및 출력
    total_penalty = update_total_penalty(penalties)
    formatted_total_penalty = f"{total_penalty:,}원"
    print(f"총금액: {formatted_total_penalty}")

if __name__ == "__main__":
    main()