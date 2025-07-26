"""
동적 필터 설정 파일
사용자별 맞춤 필터링 규칙을 정의
"""

# 기본 필터 패턴 정의
FILTER_PATTERNS = {
    "seniority": {
        "patterns": [
            ("시니어", "senior"),
            ("주니어", "junior"), 
            ("미드", "mid"),
            ("중급", "mid"),
            ("고급", "senior"),
            ("초급", "junior")
        ],
        "description": "경력 레벨"
    },
    "availability": {
        "patterns": [
            ("즉시", "available"),
            ("바로", "available"),
            ("바쁨", "busy"),
            ("고려", "considering"),
            ("검토", "considering")
        ],
        "description": "가용성"
    },
    "location": {
        "patterns": [
            ("서울", "서울"),
            ("경기", "경기"),
            ("부산", "부산"),
            ("대구", "대구"),
            ("대전", "대전"),
            ("광주", "광주"),
            ("인천", "인천"),
            ("울산", "울산"),
            ("세종", "세종")
        ],
        "suffix_patterns": [
            ("거주", ""),  # "서울거주" -> "서울"
            ("지역", ""),  # "서울지역" -> "서울"
            ("근무", "")   # "서울근무" -> "서울"
        ],
        "description": "지역"
    },
    "experience_years": {
        "patterns": [
            (r"(\d+)년", "min_years"),  # 정규식 패턴
            (r"(\d+)년이상", "min_years"),
            (r"(\d+)년 이상", "min_years"),
            (r"(\d+)년이하", "max_years"),
            (r"(\d+)년 이하", "max_years")
        ],
        "description": "경력 연차"
    },
    "companies": {
        "patterns": [
            ("네이버", "네이버"),
            ("카카오", "카카오"),
            ("쿠팡", "쿠팡"),
            ("배달의민족", "배달의민족"),
            ("토스", "토스"),
            ("당근마켓", "당근마켓"),
            ("라인", "라인"),
            ("nhn", "NHN"),
            ("구글", "Google"),
            ("페이스북", "Facebook"),
            ("마이크로소프트", "Microsoft"),
            ("애플", "Apple"),
            ("삼성전자", "삼성전자"),
            ("삼성", "삼성전자"),
            ("LG", "LG"),
            ("현대", "현대"),
            ("SK", "SK"),
            ("KT", "KT"),
            ("SKT", "SKT"),
            ("롯데", "롯데"),
            ("포스코", "포스코"),
            ("한화", "한화"),
            ("CJ", "CJ"),
            ("GS", "GS"),
            ("두산", "두산"),
            ("LS", "LS"),
            ("효성", "효성"),
            ("아시아나", "아시아나"),
            ("대우", "대우"),
            ("한진", "한진"),
            ("코오롱", "코오롱"),
            ("동부", "동부"),
            ("한라", "한라"),
            ("태영", "태영"),
            ("롯데정보통신", "롯데정보통신"),
            ("삼성SDS", "삼성SDS"),
            ("삼성전자DS", "삼성전자DS"),
            ("LG CNS", "LG CNS"),
            ("LG U+", "LG U+"),
            ("SK C&C", "SK C&C"),
            ("KT DS", "KT DS"),
            ("현대오토에버", "현대오토에버"),
            ("현대모비스", "현대모비스"),
            ("현대엔지니어링", "현대엔지니어링")
        ],
        "description": "회사 경험"
    },
    "skills": {
        "patterns": [
            ("프론트", "frontend"),
            ("프론트엔드", "frontend"),
            ("백엔드", "backend"),
            ("풀스택", "fullstack"),
            ("React", "React"),
            ("Vue", "Vue"),
            ("Angular", "Angular"),
            ("JavaScript", "JavaScript"),
            ("TypeScript", "TypeScript"),
            ("Python", "Python"),
            ("Java", "Java"),
            ("Node.js", "Node.js"),
            ("Spring", "Spring"),
            ("Django", "Django"),
            ("AWS", "AWS"),
            ("Docker", "Docker"),
            ("Kubernetes", "Kubernetes"),
            ("MySQL", "MySQL"),
            ("PostgreSQL", "PostgreSQL"),
            ("MongoDB", "MongoDB")
        ],
        "description": "기술 스택"
    },
    "salary": {
        "patterns": [
            (r"(\d+)만원", "min_salary"),
            (r"(\d+)만원이상", "min_salary"),
            (r"(\d+)만원 이상", "min_salary"),
            (r"(\d+)만원이하", "max_salary"),
            (r"(\d+)만원 이하", "max_salary")
        ],
        "description": "연봉"
    }
}

# 사용자별 맞춤 필터 설정
USER_FILTER_CONFIGS = {
    "default": {
        "enabled_filters": ["seniority", "availability", "location", "experience_years", "companies", "skills"],
        "strict_mode": False,
        "min_score_threshold": 0.3
    },
    "strict": {
        "enabled_filters": ["seniority", "availability", "location", "experience_years", "companies", "skills"],
        "strict_mode": True,
        "min_score_threshold": 0.5
    },
    "flexible": {
        "enabled_filters": ["seniority", "availability"],
        "strict_mode": False,
        "min_score_threshold": 0.1
    }
}

# 필터 우선순위 (높을수록 우선)
FILTER_PRIORITY = {
    "location": 5,      # 지역은 매우 중요
    "availability": 4,  # 가용성도 중요
    "seniority": 3,     # 경력 레벨
    "experience_years": 3,  # 경력 연차
    "companies": 2,     # 회사 경험
    "skills": 1,        # 기술 스택
    "salary": 1         # 연봉
} 