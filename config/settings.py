"""
SKAX-RA-AI-SEARCH 설정 파일
"""

import os
from pathlib import Path

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).parent.parent

# 데이터베이스 설정
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "data" / "chroma_db"))
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# 서버 설정
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 8080))

# 개발 모드
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 검색 설정
DEFAULT_SEARCH_LIMIT = 10
MAX_SEARCH_LIMIT = 100
DEFAULT_SAMPLE_COUNT = 30

# 벡터 검색 가중치
SEARCH_WEIGHTS = {
    "profile": 0.4,
    "skills": 0.35,
    "experience": 0.25
}

# 지원하는 검색 타입
SEARCH_TYPES = ["comprehensive", "profile_only"]

# 지원하는 필터 옵션
FILTER_OPTIONS = {
    "seniority": ["junior", "mid", "senior"],
    "primary_role": ["frontend", "backend", "fullstack", "devops"],
    "availability": ["available", "busy", "considering"],
    "location": ["서울", "경기", "부산", "대구", "대전", "광주", "인천"]
} 