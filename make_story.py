"""
MakeStory 통합 CLI 스크립트

사용자에게 원하는 작업(통계/플래너)을 묻고,
단일 입력 파일(input_data.txt)을 파싱하여 적절한 모듈로 전달합니다.
"""

import os
import sys

from hazel_nut_story.daily.hazel_nut_story import generate_daily_planners
from hazel_nut_story.weekly.week_record import generate_weekly_planner
from hazel_nut_story.monthly.month_record import load_activity_data, generate_monthly_story

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "input_data.txt")

def main():
    print("=" * 50)
    print("✨ MakeStory 통합 생성기 ✨")
    print("=" * 50)
    print("1. 📆 일일 플래너 생성")
    print("2. 📊 이번 주 주간 분석 (요일별/카테고리별)")
    print("3. 📈 이번 달 월간 분석 (인스타 스토리용)")
    print("=" * 50)

    choice = input("원하시는 작업의 번호를 입력하세요 (1/2/3): ").strip()

    if choice not in ['1', '2', '3']:
        print("❌ 잘못된 입력입니다. 종료합니다.")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"❌ '{INPUT_FILE}' 파일이 없습니다.")
        print("해당 파일에 카카오톡 일정 내역을 복사해 넣고 다시 실행해주세요.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # 입력 텍스트가 안내문구뿐인지 확인
    if "이 파일에 카카오톡 채팅 내역 전체를 복사해서" in text and len(text.splitlines()) < 5:
        print(f"⚠️ '{INPUT_FILE}' 파일에 데이터를 아직 넣지 않으셨습니다!")
        print("카카오톡 일정을 복사해 붙여넣고 다시 실행해주세요.")
        return

    if choice == '1':
        print("\n🚀 일일 플래너 생성을 시작합니다...")
        generate_daily_planners(text)
        print("\n✅ 모든 일일 플래너 생성 완료!")

    elif choice == '2':
        title = input("주간 플래너의 타이틀을 입력하세요 (예: 08.18 ~ 08.24) [기본값: 이번 주]: ").strip()
        if not title:
            title = "이번 주"
        
        print("\n🚀 주간 분석을 시작합니다 (AI 작동 시 다소 시간이 걸릴 수 있습니다)...")
        generate_weekly_planner(text, title=title)
        print("\n✅ 주간 플래너 생성 완료!")

    elif choice == '3':
        title = input("월간 플래너의 타이틀을 입력하세요 (예: 2026년 4월) [기본값: 이번 달]: ").strip()
        if not title:
            title = "이번 달"
            
        print("\n🚀 월간 분석을 시작합니다 (AI 작동 시 다소 시간이 걸릴 수 있습니다)...")
        plan_durations = load_activity_data(INPUT_FILE)
        generate_monthly_story(plan_durations, title=title)
        print("\n✅ 월간 플래너 생성 완료!")

if __name__ == "__main__":
    main()
