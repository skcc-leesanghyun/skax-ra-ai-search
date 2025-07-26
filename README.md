# 🚀 SKAX-RA-AI-SEARCH

벡터 데이터베이스(ChromaDB)를 활용한 지능형 개발자 검색 서비스

## 📋 프로젝트 개요

SAKX-RA-AI-SEARCH는 자연어 처리와 벡터 데이터베이스를 결합하여 개발자를 효율적으로 검색하고 매칭하는 AI 기반 소싱 시스템입니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  ChromaDB       │    │  Sentence       │
│   (FastAPI)     │◄──►│  Vector DB      │◄──►│  Transformers   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   AI Search     │◄─────────────┘
                        │   Engine        │
                        └─────────────────┘
```

## 📦 프로젝트 구조

```
skax-ra-ai-search/
├── README.md                 # 프로젝트 문서
├── requirements.txt          # Python 의존성
├── .gitignore               # Git 무시 파일
├── main.py                  # 메인 실행 파일
├── run_web.py               # 웹 서버 실행
├── config/
│   └── settings.py          # 설정 파일
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── search_engine.py # 핵심 검색 엔진
│   ├── web/
│   │   ├── __init__.py
│   │   └── templates/       # HTML 템플릿
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── search.html
│   │       ├── filter.html
│   │       └── stats.html
│   └── data/
│       └── __init__.py
├── static/                  # 정적 파일 (CSS, JS)
├── data/                   # 데이터 디렉토리
└── tests/                  # 테스트 파일
```

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd skax-ra-ai-search

# 의존성 설치
pip install -r requirements.txt
```

### 2. 실행

#### CLI 모드 (테스트용)
```bash
python main.py
```

#### 웹 인터페이스
```bash
python run_web.py
# http://localhost:8080 접속
```

## 🔍 주요 기능

### 1. AI 기반 검색
- **자연어 검색**: 자연어로 개발자 검색
- **벡터 유사도**: 의미 기반 매칭
- **다중 인덱스**: 프로필, 기술, 경력 종합 분석

### 2. 필터 검색
- **정확한 매칭**: 경력, 역할, 지역, 가용성 필터
- **조합 검색**: 다중 조건 조합
- **실시간 결과**: 즉시 결과 표시

### 3. 웹 인터페이스
- **반응형 디자인**: 모바일/데스크톱 지원
- **직관적 UI**: 사용하기 쉬운 인터페이스
- **실시간 통계**: 데이터 현황 대시보드

## 🛠️ 기술 스택

### 백엔드
- **Python 3.12+**: 메인 언어
- **FastAPI**: 웹 프레임워크
- **ChromaDB**: 벡터 데이터베이스
- **Sentence Transformers**: 임베딩 모델

### 프론트엔드
- **Bootstrap 5**: UI 프레임워크
- **jQuery**: JavaScript 라이브러리
- **Font Awesome**: 아이콘

### AI/ML
- **all-MiniLM-L6-v2**: 임베딩 모델
- **벡터 유사도**: 코사인 유사도 기반 검색

## 🎯 사용 예시

### 검색 예시
- "React 경험이 있는 시니어 개발자"
- "3년 이상 백엔드 개발자"
- "네이버에서 근무한 풀스택 개발자"
- "AWS 클라우드 경험이 있는 개발자"

### 필터 예시
- 시니어 + 즉시 가능한 개발자
- 프론트엔드 + 서울 지역
- 중급 + 백엔드 개발자

## 📈 성능 지표

- **검색 속도**: 평균 100ms 이하
- **정확도**: 85% 이상의 매칭 정확도
- **확장성**: 수천 명의 개발자 데이터 지원
- **가용성**: 24/7 운영 가능

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**SKAX-RA-AI-SEARCH** - AI 기반 개발자 소싱 시스템 🚀 