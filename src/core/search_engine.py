"""
SKAX-RA-AI-SEARCH 검색 엔진
벡터 데이터베이스 기반 개발자 검색 시스템
"""

import chromadb
import logging
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any
import numpy as np

from config.settings import DB_PATH, MODEL_NAME, SEARCH_WEIGHTS, DEFAULT_SEARCH_LIMIT, MAX_SEARCH_LIMIT
from .dynamic_filter import DynamicFilterEngine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngine:
    """AI 기반 개발자 검색 엔진"""
    
    def __init__(self, db_path: str = None, user_config: str = "default"):
        """검색 엔진 초기화"""
        self.db_path = db_path or DB_PATH
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.embedding_model = SentenceTransformer(MODEL_NAME)
        
        # 동적 필터 엔진 초기화
        self.filter_engine = DynamicFilterEngine(user_config)
        
        # 컬렉션 생성
        self.collections = self._create_collections()
        logger.info(f"검색 엔진 초기화 완료: {self.db_path} (필터 모드: {user_config})")
    
    def _create_collections(self) -> Dict[str, Any]:
        """ChromaDB 컬렉션 생성"""
        collections = {}
        
        # 프로필 컬렉션
        try:
            collections['profiles'] = self.client.get_collection("profiles")
            logger.info("기존 프로필 컬렉션 로드")
        except:
            collections['profiles'] = self.client.create_collection("profiles")
            logger.info("새 프로필 컬렉션 생성")
        
        # 기술 스택 컬렉션
        try:
            collections['skills'] = self.client.get_collection("skills")
            logger.info("기존 기술 컬렉션 로드")
        except:
            collections['skills'] = self.client.create_collection("skills")
            logger.info("새 기술 컬렉션 생성")
        
        # 경력 컬렉션
        try:
            collections['experience'] = self.client.get_collection("experience")
            logger.info("기존 경력 컬렉션 로드")
        except:
            collections['experience'] = self.client.create_collection("experience")
            logger.info("새 경력 컬렉션 생성")
        
        return collections
    
    def create_sample_data(self, count: int = 30) -> List[Dict]:
        """샘플 개발자 데이터 생성"""
        import random
        
        names = ["김철수", "이영희", "박민수", "최지영", "정현우", "한소영", "윤태호", "임수진", "강동현", "조미영"]
        locations = ["서울", "경기", "부산", "대구", "대전", "광주", "인천", "울산", "세종"]
        seniorities = ["junior", "mid", "senior"]
        roles = ["frontend", "backend", "fullstack", "devops"]
        availabilities = ["available", "busy", "considering"]
        companies = ["네이버", "카카오", "쿠팡", "배달의민족", "토스", "당근마켓", "라인", "NHN", "구글", "페이스북", "삼성전자", "LG", "현대", "SK", "KT", "롯데", "포스코", "한화", "CJ", "GS", "두산", "LS", "효성", "삼성SDS", "LG CNS", "SK C&C", "KT DS", "현대오토에버", "현대모비스", "현대엔지니어링"]
        skills = ["JavaScript", "Python", "Java", "React", "Vue", "Angular", "Node.js", "Spring", "Django", "AWS", "Docker", "Kubernetes"]
        
        developers = []
        
        for i in range(count):
            dev = {
                "developer_id": f"dev_{i+1:03d}",
                "name": random.choice(names),
                "location": random.choice(locations),
                "seniority": random.choice(seniorities),
                "primary_role": random.choice(roles),
                "years_experience": random.randint(1, 15),
                "availability": random.choice(availabilities),
                "salary_range": f"{random.randint(3, 8)}000-{random.randint(8, 15)}000",
                "skills": [
                    {
                        "name": random.choice(skills),
                        "level": random.randint(3, 5),
                        "years": random.randint(1, 8)
                    } for _ in range(random.randint(3, 6))
                ],
                "experience": [
                    {
                        "company": random.choice(companies),
                        "position": f"{random.choice(roles)} 개발자",
                        "duration_months": random.randint(6, 48),
                        "industry": "IT/소프트웨어"
                    } for _ in range(random.randint(1, 3))
                ],
                "education": {
                    "degree": "학사",
                    "major": "컴퓨터공학"
                },
                "github_stars": random.randint(0, 1000),
                "stackoverflow_reputation": random.randint(0, 5000)
            }
            developers.append(dev)
        
        return developers
    
    def add_developers(self, developers: List[Dict]) -> None:
        """개발자 데이터를 벡터 DB에 추가"""
        logger.info(f"개발자 데이터 추가 시작: {len(developers)}명")
        
        for dev in developers:
            dev_id = dev["developer_id"]
            
            # 프로필 텍스트 생성 및 임베딩
            profile_text = self._create_profile_text(dev)
            profile_embedding = self.embedding_model.encode(profile_text).tolist()
            
            # 프로필 컬렉션에 추가
            self.collections['profiles'].add(
                ids=[f"profile_{dev_id}"],
                embeddings=[profile_embedding],
                documents=[profile_text],
                metadatas=[{
                    "developer_id": dev_id,
                    "name": dev["name"],
                    "location": dev["location"],
                    "seniority": dev["seniority"],
                    "primary_role": dev["primary_role"],
                    "years_experience": dev["years_experience"],
                    "availability": dev["availability"],
                    "salary_range": dev["salary_range"]
                }]
            )
            
            # 기술 스택 추가
            for skill in dev["skills"]:
                skill_text = self._create_skill_text(dev, skill)
                skill_embedding = self.embedding_model.encode(skill_text).tolist()
                
                self.collections['skills'].add(
                    ids=[f"skill_{dev_id}_{skill['name']}"],
                    embeddings=[skill_embedding],
                    documents=[skill_text],
                    metadatas=[{
                        "developer_id": dev_id,
                        "developer_name": dev["name"],
                        "skill_name": skill["name"],
                        "skill_level": skill["level"],
                        "years_used": skill["years"],
                        "seniority": dev["seniority"]
                    }]
                )
            
            # 경력 추가
            for exp in dev["experience"]:
                exp_text = self._create_experience_text(dev, exp)
                exp_embedding = self.embedding_model.encode(exp_text).tolist()
                
                self.collections['experience'].add(
                    ids=[f"exp_{dev_id}_{exp['company']}"],
                    embeddings=[exp_embedding],
                    documents=[exp_text],
                    metadatas=[{
                        "developer_id": dev_id,
                        "developer_name": dev["name"],
                        "company": exp["company"],
                        "position": exp["position"],
                        "duration_months": exp["duration_months"],
                        "industry": exp["industry"],
                        "seniority": dev["seniority"]
                    }]
                )
        
        logger.info("벡터 DB 데이터 추가 완료")
    
    def _create_profile_text(self, dev: Dict) -> str:
        """개발자 통합 프로필 텍스트 생성"""
        skills_text = ", ".join([f"{s['name']}({s['level']}/5)" for s in dev["skills"][:5]])
        companies_text = ", ".join([exp["company"] for exp in dev["experience"]])
        
        return f"""
        {dev['name']}은 {dev['years_experience']}년 경력의 {dev['seniority']} {dev['primary_role']} 개발자입니다.
        주요 기술: {skills_text}
        경력사: {companies_text}
        위치: {dev['location']}
        가용성: {dev['availability']}
        학력: {dev['education']['degree']} {dev['education']['major']}
        GitHub 스타: {dev['github_stars']}개
        """
    
    def _create_skill_text(self, dev: Dict, skill: Dict) -> str:
        """기술 스택 상세 텍스트 생성"""
        return f"""
        {skill['name']} 기술 전문가
        숙련도: {skill['level']}/5
        사용 경험: {skill['years']}년
        개발자 레벨: {dev['seniority']}
        총 경력: {dev['years_experience']}년
        """
    
    def _create_experience_text(self, dev: Dict, exp: Dict) -> str:
        """경력 상세 텍스트 생성"""
        return f"""
        {exp['company']}에서 {exp['position']}으로 {exp['duration_months']}개월 근무
        업계: {exp['industry']}
        현재 레벨: {dev['seniority']}
        총 경력: {dev['years_experience']}년
        """
    
    def search_developers(self, query: str, search_type: str = "comprehensive", limit: int = DEFAULT_SEARCH_LIMIT) -> List[Dict]:
        """개발자 검색"""
        logger.info(f"검색 실행: '{query}' (타입: {search_type}, 제한: {limit})")
        
        # 제한 검증
        limit = min(limit, MAX_SEARCH_LIMIT)
        
        # 쿼리에서 조건 추출 (동적 필터 엔진 사용)
        extracted_filters = self.filter_engine.extract_filters(query)
        
        query_embedding = self.embedding_model.encode(query).tolist()
        
        if search_type == "profile_only":
            # 단일 인덱스 검색
            results = self.collections['profiles'].query(
                query_embeddings=[query_embedding],
                n_results=limit * 3,  # 더 많은 결과를 가져와서 필터링
                include=['documents', 'metadatas', 'distances']
            )
            filtered_results = self.filter_engine.apply_filters(self._format_simple_results(results), extracted_filters)
            return filtered_results[:limit]
        
        elif search_type == "comprehensive":
            # 다중 인덱스 검색
            results = self._multi_index_search(query_embedding, limit * 3)
            filtered_results = self.filter_engine.apply_filters(results, extracted_filters)
            return filtered_results[:limit]
    
    def _multi_index_search(self, query_embedding: List[float], limit: int) -> List[Dict]:
        """다중 인덱스 종합 검색"""
        
        # 각 인덱스에서 검색
        profile_results = self.collections['profiles'].query(
            query_embeddings=[query_embedding],
            n_results=limit * 2,
            include=['documents', 'metadatas', 'distances']
        )
        
        skill_results = self.collections['skills'].query(
            query_embeddings=[query_embedding], 
            n_results=limit * 2,
            include=['documents', 'metadatas', 'distances']
        )
        
        exp_results = self.collections['experience'].query(
            query_embeddings=[query_embedding],
            n_results=limit * 2,
            include=['documents', 'metadatas', 'distances']
        )
        
        # 개발자별 점수 집계
        developer_scores = {}
        
        # 프로필 점수
        if profile_results and 'metadatas' in profile_results and profile_results['metadatas']:
            for i, metadata in enumerate(profile_results['metadatas'][0]):
                dev_id = metadata['developer_id']
                score = 1 - profile_results['distances'][0][i]
                developer_scores[dev_id] = {
                    'metadata': metadata,
                    'profile_score': score * SEARCH_WEIGHTS['profile'],
                    'total_score': score * SEARCH_WEIGHTS['profile']
                }
        
        # 기술 점수
        if skill_results and 'metadatas' in skill_results and skill_results['metadatas']:
            for i, metadata in enumerate(skill_results['metadatas'][0]):
                dev_id = metadata['developer_id']
                score = 1 - skill_results['distances'][0][i]
                if dev_id in developer_scores:
                    developer_scores[dev_id]['skill_score'] = score * SEARCH_WEIGHTS['skills']
                    developer_scores[dev_id]['total_score'] += score * SEARCH_WEIGHTS['skills']
                else:
                    developer_scores[dev_id] = {
                        'metadata': metadata,
                        'skill_score': score * SEARCH_WEIGHTS['skills'],
                        'total_score': score * SEARCH_WEIGHTS['skills']
                    }
        
        # 경력 점수
        if exp_results and 'metadatas' in exp_results and exp_results['metadatas']:
            for i, metadata in enumerate(exp_results['metadatas'][0]):
                dev_id = metadata['developer_id']
                score = 1 - exp_results['distances'][0][i]
                if dev_id in developer_scores:
                    developer_scores[dev_id]['exp_score'] = score * SEARCH_WEIGHTS['experience']
                    developer_scores[dev_id]['total_score'] += score * SEARCH_WEIGHTS['experience']
                else:
                    developer_scores[dev_id] = {
                        'metadata': metadata,
                        'exp_score': score * SEARCH_WEIGHTS['experience'],
                        'total_score': score * SEARCH_WEIGHTS['experience']
                    }
        
        # 결과 정렬
        results = []
        for dev_id, data in developer_scores.items():
            # 경력 정보 수집
            experience_info = []
            if exp_results and 'metadatas' in exp_results and exp_results['metadatas']:
                for i, metadata in enumerate(exp_results['metadatas'][0]):
                    if metadata['developer_id'] == dev_id:
                        experience_info.append({
                            'company': metadata['company'],
                            'position': metadata['position'],
                            'duration_months': metadata['duration_months'],
                            'industry': metadata['industry']
                        })
            
            results.append({
                'developer_id': dev_id,
                'metadata': data['metadata'],
                'total_score': data['total_score'],
                'experience': experience_info
            })
        
        results.sort(key=lambda x: x['total_score'], reverse=True)
        return results
    
    def _format_simple_results(self, results) -> List[Dict]:
        """단순 검색 결과 포맷팅"""
        formatted = []
        
        # results가 유효한지 확인
        if not results or 'metadatas' not in results or not results['metadatas']:
            logger.warning("검색 결과가 비어있거나 유효하지 않습니다.")
            return formatted
        
        try:
            for i, metadata in enumerate(results['metadatas'][0]):
                formatted.append({
                    'developer_id': metadata['developer_id'],
                    'score': 1 - results['distances'][0][i],
                    'metadata': metadata,
                    'document': results['documents'][0][i]
                })
            # 매칭도 높은 순으로 정렬
            formatted.sort(key=lambda x: x['score'], reverse=True)
        except Exception as e:
            logger.error(f"검색 결과 포맷팅 오류: {e}")
        
        return formatted
    
    def search_by_filters(self, filters: Dict, limit: int = DEFAULT_SEARCH_LIMIT) -> List[Dict]:
        """필터 기반 검색"""
        logger.info(f"필터 검색: {filters}")
        
        # 더미 쿼리로 검색 후 필터링
        dummy_query = "개발자"
        dummy_embedding = self.embedding_model.encode(dummy_query).tolist()
        
        try:
            results = self.collections['profiles'].query(
                query_embeddings=[dummy_embedding],
                n_results=limit * 3,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Python-side 필터링
            filtered_results = []
            if results and 'metadatas' in results and results['metadatas']:
                for i, metadata in enumerate(results['metadatas'][0]):
                    if self._matches_filters(metadata, filters):
                        filtered_results.append({
                            'developer_id': metadata['developer_id'],
                            'score': 1 - results['distances'][0][i],
                            'metadata': metadata,
                            'document': results['documents'][0][i]
                        })
            
            filtered_results.sort(key=lambda x: x['score'], reverse=True)
            return filtered_results[:limit]
            
        except Exception as e:
            logger.error(f"필터 검색 오류: {e}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """데이터베이스 통계"""
        try:
            profile_count = self.collections['profiles'].count()
            skill_count = self.collections['skills'].count()
            exp_count = self.collections['experience'].count()
            
            return {
                "profiles": profile_count,
                "skills": skill_count,
                "experience": exp_count,
                "total": profile_count + skill_count + exp_count
            }
        except Exception as e:
            logger.error(f"통계 조회 오류: {e}")
            return {"profiles": 0, "skills": 0, "experience": 0, "total": 0}
    
    def _extract_filters_from_query(self, query: str) -> Dict[str, Any]:
        """쿼리에서 필터 조건 추출 (기존 메서드 - 호환성 유지)"""
        return self.filter_engine.extract_filters(query)
    
    def _apply_filters_to_results(self, results, filters: Dict[str, Any]) -> List[Dict]:
        """단순 검색 결과에 필터 적용 (기존 메서드 - 호환성 유지)"""
        formatted_results = self._format_simple_results(results)
        return self.filter_engine.apply_filters(formatted_results, filters)
    
    def _apply_filters_to_comprehensive_results(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """종합 검색 결과에 필터 적용 (기존 메서드 - 호환성 유지)"""
        return self.filter_engine.apply_filters(results, filters)
    
    def _matches_filters(self, metadata: Dict, filters: Dict[str, Any]) -> bool:
        """메타데이터가 필터 조건과 일치하는지 확인"""
        for key, value in filters.items():
            if key == "min_years_experience":
                if metadata.get('years_experience', 0) < value:
                    logger.debug(f"경력 조건 불일치: {metadata.get('years_experience', 0)} < {value}")
                    return False
            elif key == "companies":
                # 회사 경험 확인 (실제로는 더 복잡한 로직이 필요)
                # 여기서는 간단히 통과시킴
                pass
            elif key == "location":
                if key in metadata and metadata[key] != value:
                    logger.debug(f"지역 조건 불일치: {metadata.get(key)} != {value}")
                    return False
            elif key in metadata and metadata[key] != value:
                logger.debug(f"조건 불일치: {key} = {metadata.get(key)} != {value}")
                return False
        
        return True
    
    def get_developer_by_id(self, developer_id: str) -> Dict[str, Any]:
        """개발자 ID로 상세 정보 가져오기"""
        try:
            # 프로필 정보 가져오기
            profile_results = self.collections['profiles'].get(
                where={"developer_id": developer_id},
                include=['documents', 'metadatas']
            )

            if not profile_results['metadatas']:
                return None

            metadata = profile_results['metadatas'][0]

            # 기술 정보 가져오기
            skill_results = self.collections['skills'].get(
                where={"developer_id": developer_id},
                include=['documents', 'metadatas']
            )

            # 경력 정보 가져오기
            exp_results = self.collections['experience'].get(
                where={"developer_id": developer_id},
                include=['documents', 'metadatas']
            )

            # 개발자 데이터 구성
            developer = {
                "developer_id": developer_id,
                "name": metadata["name"],
                "location": metadata["location"],
                "seniority": metadata["seniority"],
                "primary_role": metadata["primary_role"],
                "years_experience": metadata["years_experience"],
                "availability": metadata["availability"],
                "salary_range": metadata["salary_range"],
                "skills": [],
                "experience": [],
                "education": {
                    "degree": "학사",
                    "major": "컴퓨터공학"
                },
                "github_stars": 0,
                "stackoverflow_reputation": 0
            }

            # 기술 정보 추가
            if skill_results and 'metadatas' in skill_results and skill_results['metadatas']:
                for i, skill_metadata in enumerate(skill_results['metadatas']):
                    developer["skills"].append({
                        "name": skill_metadata["skill_name"],
                        "level": skill_metadata["skill_level"],
                        "years": skill_metadata["years_used"]
                    })

            # 경력 정보 추가
            if exp_results and 'metadatas' in exp_results and exp_results['metadatas']:
                for i, exp_metadata in enumerate(exp_results['metadatas']):
                    developer["experience"].append({
                        "company": exp_metadata["company"],
                        "position": exp_metadata["position"],
                        "duration_months": exp_metadata["duration_months"],
                        "industry": exp_metadata["industry"]
                    })

            logger.info(f"개발자 정보 조회: {developer_id}")
            return developer

        except Exception as e:
            logger.error(f"개발자 정보 조회 오류: {e}")
            return None
