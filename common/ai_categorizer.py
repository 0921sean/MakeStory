"""
AI 기반 활동 카테고리 분류기

Gemini API를 사용하여 미지의 활동을 정해진 카테고리로 자동 분류합니다.
한 번 분류한 결과는 캐시(category_cache.json)에 저장하여 API 호출 비용 및 시간을 절약합니다.
"""

import json
import os
import sys

# 프로젝트 루트 및 캐시 파일 경로 
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(PROJECT_ROOT, "hazel_nut_story", "weekly", "category_cache.json")

# 분류할 기본 카테고리 목록
STANDARD_CATEGORIES = [
    "코딩", "글쓰기", "언어", "헬스", "유익한 영상", 
    "미팅", "연구/논문", "학교 수업", "동아리", "스터디", "퀀트", "기타"
]

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

_category_cache = load_cache()

def get_category_with_ai(plan_name: str) -> str:
    """Gemini API를 호출하여 카테고리를 분류합니다."""
    # 환경변수에서 키 확인
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"⚠️ [AI 경고] GEMINI_API_KEY 환경변수가 없습니다. '{plan_name}'을(를) '기타'로 임시 분류합니다.")
        return "기타"

    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
다음은 사용자의 일정/목표 이름입니다: "{plan_name}"
이 일정을 다음 제공된 카테고리 중 가장 적합한 것 하나로만 분류해 주세요.
카테고리: {', '.join(STANDARD_CATEGORIES)}

[분류 가이드라인 (중요)]
- "딥실"(딥러닝실험), "물전", "중문이", "고문상", "데구", "컴구", "바전공", "주채파", "계량경제학", "운영체제론" 등 대학교 과목 이름은 '학교 수업'으로 분류하세요.
- "SURI", "BOTA", "GTC", "코라밸리" 등은 '동아리'로 분류하세요.
- "과제"나 "렢 작성"(레포트)이 붙어있더라도 위의 학교 수업과 연관되면 '학교 수업' 또는 '연구/논문'으로 분류하세요.
- 알고리즘, CS 공부 등은 '코딩'에 가깝습니다.

반드시 카테고리 목록에 있는 이름 중 하나만 정확히 출력해야 하며, 따옴표나 부가 설명 없이 카테고리 이름만 출력하세요.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        result = response.text.strip()
        # 반환값이 지정된 카테고리 내에 있는지 한 번 더 검증
        for cat in STANDARD_CATEGORIES:
            if cat in result:
                return cat
                
        return "기타"  # 매칭 실패 시 기본값
    except Exception as e:
        print(f"⚠️ [AI 에러] API 호출 중 오류 발생: {e}")
        return "기타"

def map_category(plan_name: str) -> str:
    """
    활동명을 입력받아 카테고리를 반환합니다.
    (1) 캐시 확인 -> (2) 없으면 AI 분류 -> (3) 캐시 저장 후 반환
    """
    # 1. 완벽한 일치 확인
    if plan_name in _category_cache:
        return _category_cache[plan_name]
        
    # 2. 부분 일치 휴리스틱 (비용 절약을 위해 명확한 키워드는 미리 필터링)
    # 기존 CATEGORY_MAP을 보완하는 차원
    heuristic_map = {
        "헬스": "헬스",
        "운동": "헬스",
        "언어": "언어",
        "글쓰기": "글쓰기",
        "코테": "코딩",
        "코딩": "코딩",
        "영상": "유익한 영상",
        "미팅": "미팅",
        "회의": "미팅",
        "논문": "연구/논문",
        "연구": "연구/논문",
        "딥실": "학교 수업",
        "데구": "학교 수업",
        "컴구": "학교 수업",
        "고문상": "학교 수업",
        "중문이": "학교 수업",
        "바전공": "학교 수업",
        "물전": "학교 수업",
        "SURI": "동아리",
        "GTC": "동아리",
        "BOTA": "동아리",
        "코라밸리": "동아리",
    }
    
    for kw, cat in heuristic_map.items():
        if kw in plan_name:
            _category_cache[plan_name] = cat
            save_cache(_category_cache)
            return cat
            
    # 3. AI 기반 분류
    print(f"🤖 [AI 분석 중] 새로운 일정 감지: '{plan_name}' 분류 중...")
    category = get_category_with_ai(plan_name)
    print(f"   => '{category}'(으)로 분류되었습니다.")
    
    # 캐시 저장
    _category_cache[plan_name] = category
    save_cache(_category_cache)
    
    return category

# 테스트용 코드
if __name__ == "__main__":
    test_plans = ["사이드프로젝트 개발", "친구랑 저녁 약속", "BOTA 질문답변"]
    for plan in test_plans:
        print(f"{plan} -> {map_category(plan)}")
