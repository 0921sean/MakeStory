# MakeStory

카카오톡 채팅 로그 기반의 **개인 생산성 관리 자동화 도구 모음**입니다.

## 프로젝트 구조

```
MakeStory/
├── common/                    # 공통 유틸리티
│   ├── config.py              # 전역 설정 (경로, 색상, 멤버 목록)
│   └── time_utils.py          # 시간 파싱/변환 함수
├── hazel_nut_story/           # 플래너 이미지 자동 생성
│   ├── daily/
│   │   └── hazel_nut_story.py # 일일 플래너 생성
│   ├── weekly/
│   │   ├── week_record.py     # 주간 기록 이미지 생성
│   │   └── category_cache.json # AI 분류 캐시 내역
│   └── monthly/
│       ├── month_record.py    # 월간 인스타 스토리 생성
│       └── july_cal.py        # 주차별 집중 시간 계산
├── healthfam/                 # 운동 벌금 추적
│   └── healthfam.py           # 운동 횟수 파싱 → 벌금 계산
├── kora_valley/               # KorA Valley 목표 트래킹
│   ├── kora_valley_tracking.py # 계획/완료 → 엑셀 자동 업데이트
│   ├── create_db.py           # DB 시트 초기 생성
│   └── blur_pictures.py       # 이미지 블러 처리
├── .gitignore
├── requirements.txt
└── README.md
```

## 모듈 설명

### 🗓️ hazel_nut_story — 플래너 자동 생성

카톡 채팅 로그 형식의 텍스트를 파싱하여 **일간/주간/월간 플래너 이미지**를 자동 생성합니다.

```bash
# 일일 플래너 생성
python hazel_nut_story/hazel_nut_story.py

# 주간 기록 이미지 생성
python hazel_nut_story/week_record.py weekly_data.txt

# 월간 인스타 스토리 생성
python hazel_nut_story/month_record.py july.txt
```

### 💪 healthfam — 운동 벌금 추적

카톡 채팅 로그에서 **주 3회 운동 여부**를 추적하고 벌금을 자동 계산합니다.

```bash
python healthfam/healthfam.py
```

### 📊 kora_valley — KorA Valley 목표 트래킹

카톡 채팅에서 멤버들의 **계획 작성 및 완료(✅)**를 파싱하여 엑셀에 자동 반영합니다.

```bash
python kora_valley/kora_valley_tracking.py
```

## 설정

공통 설정은 `common/config.py`에서 관리합니다:

- **폰트 경로**: `FONT_SAMANCO`, `FONT_HALLASAN`
- **색상 팔레트**: `COLOR_12`, `COLOR_7`
- **KorA Valley 멤버**: `KORA_NAME_MAP`
- **Healthfam 멤버**: `HEALTHFAM_MEMBERS`

## 설치

```bash
pip install -r requirements.txt
```
