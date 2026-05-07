import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path):
    print(f"\n▶️ [{script_path}] 실행 시작...")
    result = subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    if result.returncode == 0:
        print(f"✅ [{script_path}] 완료")
    else:
        print(f"❌ [{script_path}] 실패 (에러 코드: {result.returncode})")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 일괄 실행 스크립트 (플래너 + 코라밸리 + 헬스팸)")
    print("=" * 60)
    
    scripts = [
        "hazel_nut_story/daily/hazel_nut_story.py",
        "kora_valley/kora_valley_tracking.py",
        "healthfam/healthfam.py"
    ]
    
    for script in scripts:
        run_script(script)
        
    print("\n" + "=" * 60)
    print("✨ 모든 스크립트 실행이 완료되었습니다! ✨")
    print("=" * 60)
