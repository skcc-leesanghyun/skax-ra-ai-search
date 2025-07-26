"""
동적 필터 엔진
설정 파일을 기반으로 유연한 필터링 제공
"""

import re
import logging
from typing import Dict, List, Any, Optional
from config.filter_config import FILTER_PATTERNS, USER_FILTER_CONFIGS, FILTER_PRIORITY

logger = logging.getLogger(__name__)

class DynamicFilterEngine:
    """동적 필터 엔진"""
    
    def __init__(self, user_config: str = "default"):
        """필터 엔진 초기화"""
        self.user_config = user_config
        self.config = USER_FILTER_CONFIGS.get(user_config, USER_FILTER_CONFIGS["default"])
        self.enabled_filters = self.config["enabled_filters"]
        self.strict_mode = self.config["strict_mode"]
        self.min_score_threshold = self.config["min_score_threshold"]
        
        logger.info(f"동적 필터 엔진 초기화: {user_config} 모드")
    
    def extract_filters(self, query: str) -> Dict[str, Any]:
        """쿼리에서 필터 조건 추출"""
        filters = {}
        query_lower = query.lower()
        
        logger.debug(f"쿼리 분석: '{query}' (소문자: '{query_lower}')")
        logger.debug(f"활성화된 필터: {self.enabled_filters}")
        
        for filter_type in self.enabled_filters:
            if filter_type not in FILTER_PATTERNS:
                logger.debug(f"필터 타입 '{filter_type}' 패턴 없음")
                continue
                
            pattern_config = FILTER_PATTERNS[filter_type]
            logger.debug(f"필터 타입 '{filter_type}' 패턴 분석 시작")
            extracted_value = self._extract_filter_value(query, query_lower, pattern_config, filter_type)
            
            if extracted_value is not None:
                filters[filter_type] = extracted_value
                logger.debug(f"필터 추출: {filter_type} = {extracted_value}")
            else:
                logger.debug(f"필터 타입 '{filter_type}'에서 값 추출 실패")
        
        logger.info(f"추출된 필터: {filters}")
        return filters
    
    def _extract_filter_value(self, query: str, query_lower: str, pattern_config: Dict, filter_type: str) -> Any:
        """특정 필터 타입의 값 추출"""
        patterns = pattern_config.get("patterns", [])
        
        for pattern, value in patterns:
            if filter_type == "experience_years" or filter_type == "salary":
                # 정규식 패턴 처리
                match = re.search(pattern, query)
                if match:
                    number = int(match.group(1))
                    if "min_years" in value:
                        return {"min": number}
                    elif "max_years" in value:
                        return {"max": number}
                    elif "min_salary" in value:
                        return {"min": number}
                    elif "max_salary" in value:
                        return {"max": number}
            else:
                # 일반 문자열 패턴 처리
                if pattern in query:
                    logger.debug(f"패턴 매칭: '{pattern}' in '{query}' -> {value}")
                    # 접미사 패턴 확인
                    suffix_patterns = pattern_config.get("suffix_patterns", [])
                    for suffix, suffix_value in suffix_patterns:
                        if pattern + suffix in query:
                            return value + suffix_value
                    return value
                else:
                    logger.debug(f"패턴 미매칭: '{pattern}' not in '{query}'")
        
        return None
    
    def apply_filters(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """결과에 필터 적용"""
        if not filters:
            return results
        
        filtered_results = []
        
        for result in results:
            if self._matches_filters(result, filters):
                filtered_results.append(result)
        
        # 우선순위에 따른 정렬
        filtered_results = self._sort_by_priority(filtered_results, filters)
        
        logger.info(f"필터 적용: {len(results)} -> {len(filtered_results)}개")
        return filtered_results
    
    def _matches_filters(self, result: Dict, filters: Dict[str, Any]) -> bool:
        """결과가 필터 조건과 일치하는지 확인"""
        metadata = result.get('metadata', {})
        
        # 필터 조건에 맞지 않는 항목 수 계산
        mismatch_count = 0
        total_filters = len(filters)
        
        for filter_type, filter_value in filters.items():
            # 회사 경험 필터링은 별도 처리
            if filter_type == "companies":
                if not self._check_company_filter(result, filter_value):
                    if self.strict_mode:
                        return False
                    mismatch_count += 1
            else:
                if not self._check_single_filter(metadata, filter_type, filter_value):
                    if self.strict_mode:
                        return False
                    mismatch_count += 1
        
        # 엄격 모드가 아닌 경우 점수 조정 (한 번만 적용)
        if mismatch_count > 0 and not self.strict_mode:
            # 기존 점수 유지하되, 필터 불일치 비율만큼만 차감
            original_score = result.get('total_score', result.get('score', 1.0))
            penalty = (mismatch_count / total_filters) * 0.5  # 최대 50% 차감
            adjusted_score = original_score * (1 - penalty)
            # 점수가 0.1 미만이 되지 않도록 보장
            result['total_score'] = max(adjusted_score, 0.1)
            if 'score' in result:
                result['score'] = max(adjusted_score, 0.1)
        else:
            # 모든 필터가 일치하는 경우 점수 보정
            original_score = result.get('total_score', result.get('score', 1.0))
            result['total_score'] = min(original_score, 1.0)  # 최대 100%
            if 'score' in result:
                result['score'] = min(original_score, 1.0)
        
        return True
    
    def _check_single_filter(self, metadata: Dict, filter_type: str, filter_value: Any) -> bool:
        """단일 필터 조건 확인"""
        if filter_type == "experience_years":
            years = metadata.get('years_experience', 0)
            if isinstance(filter_value, dict):
                if 'min' in filter_value and years < filter_value['min']:
                    return False
                if 'max' in filter_value and years > filter_value['max']:
                    return False
            return True
        
        elif filter_type == "salary":
            # 연봉 필터링 (실제 구현 시 salary_range 파싱 필요)
            return True
        
        elif filter_type == "companies":
            # 회사 경험 필터링은 _check_company_filter에서 처리
            return True
        
        elif filter_type == "skills":
            # 기술 스택 필터링 - primary_role과 비교
            primary_role = metadata.get('primary_role', '').lower()
            if isinstance(filter_value, str):
                skill_lower = filter_value.lower()
                # 프론트엔드 관련 기술
                if skill_lower in ['frontend', '프론트', '프론트엔드', 'react', 'vue', 'angular', 'javascript', 'typescript']:
                    return primary_role in ['frontend', 'fullstack']
                # 백엔드 관련 기술
                elif skill_lower in ['backend', '백엔드', 'java', 'python', 'spring', 'django', 'node.js']:
                    return primary_role in ['backend', 'fullstack']
                # 풀스택 관련 기술
                elif skill_lower in ['fullstack', '풀스택']:
                    return primary_role == 'fullstack'
                # 풀스택은 모든 기술에 매칭
                elif primary_role == 'fullstack':
                    return True
            return False
        
        else:
            # 기본 필터 (seniority, availability, location)
            if filter_type in metadata:
                return metadata[filter_type] == filter_value
        
        return True
    
    def _check_company_filter(self, result: Dict, filter_value: Any) -> bool:
        """회사 경험 필터링 확인"""
        # experience 데이터에서 확인
        if 'experience' in result:
            experience_data = result['experience']
            if isinstance(experience_data, list):
                # experience가 리스트인 경우 (경력 정보 배열)
                for exp in experience_data:
                    if isinstance(exp, dict) and 'company' in exp:
                        company_name = exp['company'].lower()
                        if isinstance(filter_value, str):
                            company_lower = filter_value.lower()
                            if company_lower in company_name:
                                return True
            elif isinstance(experience_data, str):
                # experience가 문자열인 경우
                experience_text = experience_data.lower()
                if isinstance(filter_value, str):
                    company_lower = filter_value.lower()
                    return company_lower in experience_text
        
        # metadata에서 company 확인
        metadata = result.get('metadata', {})
        if 'company' in metadata:
            company_name = metadata['company']
            if isinstance(company_name, str):
                company_name = company_name.lower()
                if isinstance(filter_value, str):
                    company_lower = filter_value.lower()
                    return company_lower in company_name
        
        # 둘 다 없는 경우 기본적으로 True 반환
        return True
    
    def _sort_by_priority(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """우선순위에 따른 정렬"""
        def priority_score(result):
            score = 0
            metadata = result.get('metadata', {})
            
            for filter_type, filter_value in filters.items():
                priority = FILTER_PRIORITY.get(filter_type, 1)
                if self._check_single_filter(metadata, filter_type, filter_value):
                    score += priority
            
            return score
        
        # 우선순위 점수로 정렬
        results.sort(key=priority_score, reverse=True)
        return results
    
    def get_filter_info(self, filters: Dict[str, Any]) -> str:
        """필터 정보를 사용자 친화적 텍스트로 변환"""
        if not filters:
            return ""
        
        filter_labels = {
            'seniority': '경력 레벨',
            'availability': '가용성',
            'location': '지역',
            'experience_years': '경력 연차',
            'companies': '회사 경험',
            'skills': '기술 스택',
            'salary': '연봉'
        }
        
        filter_texts = []
        for filter_type, value in filters.items():
            label = filter_labels.get(filter_type, filter_type)
            
            if filter_type == "experience_years":
                if isinstance(value, dict):
                    if 'min' in value:
                        filter_texts.append(f"{label}: {value['min']}년 이상")
                    if 'max' in value:
                        filter_texts.append(f"{label}: {value['max']}년 이하")
            elif filter_type == "salary":
                if isinstance(value, dict):
                    if 'min' in value:
                        filter_texts.append(f"{label}: {value['min']}만원 이상")
                    if 'max' in value:
                        filter_texts.append(f"{label}: {value['max']}만원 이하")
            else:
                filter_texts.append(f"{label}: {value}")
        
        return ", ".join(filter_texts)
    
    def update_user_config(self, new_config: Dict[str, Any]):
        """사용자 설정 업데이트"""
        self.config.update(new_config)
        self.enabled_filters = self.config["enabled_filters"]
        self.strict_mode = self.config["strict_mode"]
        self.min_score_threshold = self.config["min_score_threshold"]
        
        logger.info(f"사용자 설정 업데이트: {new_config}")
    
    def add_custom_pattern(self, filter_type: str, pattern: str, value: Any):
        """사용자 정의 패턴 추가"""
        if filter_type not in FILTER_PATTERNS:
            FILTER_PATTERNS[filter_type] = {"patterns": [], "description": "사용자 정의"}
        
        FILTER_PATTERNS[filter_type]["patterns"].append((pattern, value))
        logger.info(f"사용자 정의 패턴 추가: {filter_type} - {pattern} -> {value}")
