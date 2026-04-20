import os
import time
import requests
import hashlib
import hmac
import base64
import re
from typing import List, Optional, Dict, Tuple
from curl_cffi import requests as cffi_requests
from dotenv import load_dotenv
from src.utils.llm_provider import BaseLLMProvider, get_llm_provider
from src.processors.trademark_blacklist import contains_trademark, filter_trademarked_keywords

from src.processors.keyword_stop_words import KEYWORD_STOP_WORDS

load_dotenv()

class KeywordProcessor:
    """
    강화된 키워드 프로세서.
    
    3-Phase 워크플로우:
        Phase 1: 다각도 시드(Seed) 수집 - 상품명 변형 + 다회 검색
        Phase 2: 경쟁도 기반 필터링 - 네이버 API 데이터 활용 + 불용어(Stop Words) 제거
        Phase 3: 상표권 이중 검증 + LLM 최종 큐레이션
    """
    
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None, api_keys: dict = None):
        if api_keys is None:
            api_keys = {}
        # Naver Ad API Config (검색광고 API)
        self.naver_base_url = os.getenv("NAVER_API_BASE_URL", "https://api.searchad.naver.com")
        self.naver_api_key = api_keys.get("naver_api_key") or os.getenv("NAVER_API_KEY")
        self.naver_secret_key = api_keys.get("naver_secret_key") or os.getenv("NAVER_SECRET_KEY")
        self.naver_customer_id = api_keys.get("naver_customer_id") or os.getenv("NAVER_CUSTOMER_ID")
        
        # LLM Provider
        if llm_provider is None:
            self.llm_provider = get_llm_provider("gemini")
        else:
            self.llm_provider = llm_provider

    # ============================================================
    # Public API (기존 시그니처 유지)
    # ============================================================

    def process_keywords(self, product_name: str, prompt_template: str = None) -> str:
        """
        강화된 키워드 생성 워크플로우.
        
        Args:
            product_name: 가공된 상품명
            prompt_template: (옵션) 사용자 커스텀 프롬프트 (최종 큐레이션용)
            
        Returns:
            콤마로 구분된 키워드 문자열
        """
        print(f"\n{'='*60}")
        print(f"[키워드 생성 시작] 상품명: {product_name}")
        print(f"{'='*60}")
        
        # ── Phase 1: 다각도 시드 수집 ──
        print("\n📌 Phase 1: 다각도 시드 수집")
        seed_keywords_with_data = self._collect_seeds_multi_round(product_name)
        
        if not seed_keywords_with_data:
            print("⚠️ 시드 키워드를 수집하지 못했습니다.")
            return ""
        
        print(f"   → 총 {len(seed_keywords_with_data)}개 후보 키워드 수집 완료")
        
        # ── Phase 2: 경쟁도 기반 필터링 ──
        print("\n📌 Phase 2: 경쟁도 기반 필터링")
        filtered_keywords = self._filter_by_competition(seed_keywords_with_data)
        print(f"   → 필터링 후 {len(filtered_keywords)}개 키워드 생존")
        
        if not filtered_keywords:
            # 필터링 후 너무 적으면 경쟁도 필터 완화 (키워드명만이라도 사용)
            print("   ⚠️ 경쟁도 필터 결과가 너무 적어 원본 키워드명을 사용합니다.")
            filtered_keywords = [
                {"keyword": item["keyword"], "compIdx": "불명", "totalQcCnt": 0}
                for item in seed_keywords_with_data
            ]
        
        # ── Phase 3: 상표권 검증 + LLM 큐레이션 ──
        print("\n📌 Phase 3: 상표권 검증 + LLM 큐레이션")
        final_keywords = self._finalize_keywords(product_name, filtered_keywords, prompt_template)
        
        # 최대 10개로 제한
        final_keywords = final_keywords[:10]
        
        print(f"\n{'='*60}")
        print(f"[결과] 최종 키워드 ({len(final_keywords)}개): {final_keywords}")
        print(f"{'='*60}\n")
        
        return ", ".join(final_keywords)

    # ============================================================
    # Phase 1: 다각도 시드 수집
    # ============================================================

    def _collect_seeds_multi_round(self, product_name: str) -> List[Dict]:
        """
        원본 상품명 + LLM 변형 상품명으로 다회 검색하여 시드 키워드를 수집합니다.
        
        Returns:
            List[Dict]: [{"keyword": "...", "monthlyPcQcCnt": N, "monthlyMobileQcCnt": N, "compIdx": "높음/중간/낮음"}, ...]
        """
        all_keywords = {}  # keyword -> data dict (중복 제거용)
        
        # Round 1: 원본 상품명으로 검색
        print(f"   [Round 1] 원본 상품명: '{product_name}'")
        round1_results = self._search_naver_keywords_with_data(product_name)
        round1_coupang = self._get_coupang_related_keywords(product_name)
        
        for item in round1_results:
            all_keywords[item["keyword"]] = item
        
        # 쿠팡 키워드는 검색량 데이터 없이 키워드명만 추가
        for kw in round1_coupang:
            if kw not in all_keywords:
                all_keywords[kw] = {"keyword": kw, "monthlyPcQcCnt": 0, "monthlyMobileQcCnt": 0, "compIdx": "불명"}
        
        print(f"      → {len(round1_results)}개 (네이버) + {len(round1_coupang)}개 (쿠팡)")
        
        # Round 2~3: LLM으로 상품명 변형 후 재검색
        variations = self._generate_product_name_variations(product_name)
        
        for i, variation in enumerate(variations, start=2):
            print(f"   [Round {i}] 변형 상품명: '{variation}'")
            round_results = self._search_naver_keywords_with_data(variation)
            round_coupang = self._get_coupang_related_keywords(variation)
            
            for item in round_results:
                if item["keyword"] not in all_keywords:
                    all_keywords[item["keyword"]] = item
            
            for kw in round_coupang:
                if kw not in all_keywords:
                    all_keywords[kw] = {"keyword": kw, "monthlyPcQcCnt": 0, "monthlyMobileQcCnt": 0, "compIdx": "불명"}
            
            print(f"      → {len(round_results)}개 (네이버) + {len(round_coupang)}개 (쿠팡)")
        
        return list(all_keywords.values())

    def _generate_product_name_variations(self, product_name: str) -> List[str]:
        """
        LLM을 사용하여 상품명의 동의어/약칭/다른 관점 변형을 2~3개 생성합니다.
        """
        if not self.llm_provider.is_configured():
            return []
        
        try:
            prompt = f"""역할: 온라인 쇼핑 키워드 전문가
작업: 다음 상품명을 소비자가 검색할 수 있는 다른 표현으로 2~3개 변형해주세요.

규칙:
1. 동의어, 약칭, 다른 관점의 표현을 사용
2. 브랜드명은 절대 포함하지 마세요
3. 각 변형은 자연스러운 검색어 형태여야 합니다
4. 결과만 출력 (한 줄에 하나씩, 번호 없이)

상품명: "{product_name}"
변형:"""
            
            result = self.llm_provider.generate_content(prompt)
            variations = [v.strip().strip('-').strip('•').strip() for v in result.strip().split('\n') if v.strip()]
            # 최대 3개까지만
            variations = variations[:3]
            print(f"   [LLM] 상품명 변형 생성: {variations}")
            return variations
            
        except Exception as e:
            print(f"   ⚠️ 상품명 변형 생성 실패: {e}")
            return []

    def _search_naver_keywords_with_data(self, keyword: str) -> List[Dict]:
        """
        네이버 검색광고 API로 연관 키워드 + 검색량/경쟁도 데이터를 함께 수집합니다.
        
        Returns:
            List[Dict]: [{"keyword": "...", "monthlyPcQcCnt": N, "monthlyMobileQcCnt": N, "compIdx": "높음"}, ...]
        """
        if not (self.naver_api_key and self.naver_secret_key):
            return []
        
        try:
            uri = '/keywordstool'
            method = 'GET'
            # Naver API may reject keywords with spaces in some contexts or treat them as invalid.
            # Removing spaces for the search query often helps for compound words in Korean.
            clean_keyword = keyword.replace(" ", "")
            params = {'hintKeywords': clean_keyword, 'showDetail': '1'}
            headers = self._get_naver_header(method, uri)
            resp = requests.get(self.naver_base_url + uri, params=params, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get('keywordList', []):
                    kw = item.get('relKeyword', '')
                    if not kw:
                        continue
                    
                    # 검색량 데이터 추출 (< 10 등 문자열일 수 있음)
                    pc_qc = item.get('monthlyPcQcCnt', 0)
                    mobile_qc = item.get('monthlyMobileQcCnt', 0)
                    
                    # "< 10" 같은 문자열 처리
                    if isinstance(pc_qc, str):
                        pc_qc = 5  # "< 10"의 경우 보수적으로 5로 처리
                    if isinstance(mobile_qc, str):
                        mobile_qc = 5
                    
                    results.append({
                        "keyword": kw,
                        "monthlyPcQcCnt": pc_qc,
                        "monthlyMobileQcCnt": mobile_qc,
                        "totalQcCnt": pc_qc + mobile_qc,
                        "compIdx": item.get('compIdx', '불명'),  # 높음/중간/낮음
                    })
                return results
            else:
                try:
                    error_msg = resp.json().get('message', 'Unknown Error')
                    print(f"      ⚠️ 네이버 API 응답 오류 ({resp.status_code}): {error_msg}")
                except:
                    print(f"      ⚠️ 네이버 API 응답 오류 ({resp.status_code})")
                return []
        except Exception as e:
            print(f"      ⚠️ 네이버 API 호출 실패: {e}")
            return []

    def _get_coupang_related_keywords(self, keyword: str) -> List[str]:
        """쿠팡 연관 검색어 수집"""
        try:
            base_url = "https://www.coupang.com/n-api/web-adapter/search"
            params = {"keyword": keyword}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
            res = cffi_requests.get(base_url, params=params, headers=headers, impersonate="chrome124", timeout=10)
            if res.status_code != 200:
                return []
            data = res.json()
            return [item.get("keyword") for item in data if item.get("keyword")]
        except Exception:
            return []

    # ============================================================
    # Phase 2: 경쟁도 기반 필터링
    # ============================================================

    def _filter_by_competition(self, keywords_data: List[Dict]) -> List[Dict]:
        """
        경쟁도와 검색량 데이터를 기반으로 소상공인에 적합한 키워드를 필터링합니다.
        
        필터링 기준:
        - 불용어(Stop Words) 포함 키워드 제거
        - 경쟁도 "높음" 키워드 제거 (대기업 독점 영역)
        - 단일 단어 키워드 제거 (너무 광범위)
        - 롱테일 키워드(2단어 이상) 우선
        """
        filtered = []
        removed_reasons = []
        
        for item in keywords_data:
            kw = item["keyword"]
            comp_idx = item.get("compIdx", "불명")
            total_qc = item.get("totalQcCnt", 0)
            
            # 0. 불용어(Stop Words) 필터링
            if self._is_stop_word(kw):
                 removed_reasons.append(f"   🚫 '{kw}' → 불용어 포함")
                 continue

            # 1. 경쟁도 "높음" 제거
            if comp_idx == "높음":
                removed_reasons.append(f"   🚫 '{kw}' → 경쟁도 높음")
                continue
            
            # 2. 단일 글자 키워드 제거 (너무 광범위)
            if len(kw.replace(" ", "")) <= 1:
                removed_reasons.append(f"   🚫 '{kw}' → 너무 짧음")
                continue
            
            # 3. 단일 단어이면서 2글자 이하인 경우 제거
            words = kw.split()
            if len(words) == 1 and len(kw) <= 2:
                removed_reasons.append(f"   🚫 '{kw}' → 단일 짧은 단어")
                continue
            
            # 롱테일 보너스 점수 계산
            longtail_score = 0
            if len(words) >= 3:
                longtail_score = 2  # 3단어 이상
            elif len(words) >= 2:
                longtail_score = 1  # 2단어
            
            item["longtail_score"] = longtail_score
            item["quality_score"] = longtail_score + (1 if comp_idx == "낮음" else 0)
            
            filtered.append(item)
        
        # 디버그: 제거된 키워드 일부 출력 (최대 10개)
        if removed_reasons:
            for reason in removed_reasons[:10]:
                print(reason)
            if len(removed_reasons) > 10:
                print(f"   ... 외 {len(removed_reasons) - 10}개 추가 제거")
        
        # 품질 점수 기준 정렬 (높은 점수 우선)
        filtered.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        return filtered

    # ============================================================
    # Phase 3: 상표권 검증 + LLM 최종 큐레이션
    # ============================================================

    def _finalize_keywords(self, product_name: str, keywords_data: List[Dict], prompt_template: str = None) -> List[str]:
        """
        상표권 이중 검증 + LLM 최종 큐레이션을 수행합니다.
        """
        keyword_names = [item["keyword"] for item in keywords_data]
        
        # ── Step 1: 상표권 블랙리스트 1차 필터 ──
        safe_keywords, removed_keywords = filter_trademarked_keywords(keyword_names)
        
        if removed_keywords:
            print(f"   [블랙리스트] {len(removed_keywords)}개 상표 키워드 제거: {removed_keywords[:5]}{'...' if len(removed_keywords) > 5 else ''}")
        
        print(f"   [블랙리스트] {len(safe_keywords)}개 키워드 통과")
        
        if not safe_keywords:
            return []
        
        # 안전한 키워드에 대한 데이터 재매핑
        safe_data = [item for item in keywords_data if item["keyword"] in safe_keywords]
        
        # ── Step 2: LLM 상표권 2차 검증 + 최종 큐레이션 ──
        if not self.llm_provider.is_configured():
            return safe_keywords[:10]
        
        final_keywords = self._curate_with_llm(product_name, safe_data, prompt_template)
        
        return final_keywords

    def _curate_with_llm(self, product_name: str, keywords_data: List[Dict], prompt_template: str = None) -> List[str]:
        """
        LLM으로 상표권 2차 검증 + 최종 키워드 큐레이션을 동시에 수행합니다.
        """
        try:
            # 키워드 + 경쟁도 데이터를 함께 포맷
            keyword_info_lines = []
            for item in keywords_data:
                kw = item["keyword"]
                comp = item.get("compIdx", "불명")
                total = item.get("totalQcCnt", 0)
                keyword_info_lines.append(f"- {kw} (경쟁도: {comp}, 월 검색수: {total})")
            
            keywords_info = "\n".join(keyword_info_lines)
            # gpt-5-nano is unstable. Use Simple Prompt + Retry Logic.
            all_keyword_names = ", ".join([item["keyword"] for item in keywords_data])
            
            prompt_v1 = f"""Select 10 safe keywords from this list for '{product_name}'.
List: {all_keyword_names}
Constraint:
- No generic terms like 'Option', 'Random', 'Unit' (e.g. 1개, 1Set), 'Shipping' terms.
- No trademarks/brands.
Return comma-separated string."""

            prompt_v2 = f"""Extract 10 keywords for '{product_name}' from: {all_keyword_names}.
Safety: No brands. No generic options (color/size/unit).
Format: Comma separated."""

            prompts = [prompt_v1, prompt_v2, prompt_v1] # Retry sequence
            
            final = []
            
            for attempt, attempt_prompt in enumerate(prompts):
                if attempt > 0:
                    print(f"   ⚠️ LLM Attempt {attempt+1} (Retrying)...")
                
                try:
                    result = self.llm_provider.generate_content(attempt_prompt)
                    # print(f"   [DEBUG] LLM Result: {result}") # Verbose debug
                    
                    if not result:
                        continue
                        
                    # Normalize and split
                    normalized = result.replace('\n', ',')
                    candidates = [k.strip() for k in normalized.split(',') if k.strip()]
                    
                    # Filter trademarks and stop words
                    temp_final = []
                    for kw in candidates:
                        # Basic cleanup
                        kw = re.sub(r'^[\d+\.\-\*\•\s]+', '', kw).strip()
                        if not kw: continue
                        
                        if contains_trademark(kw):
                            # print(f"   ⚠️ Removed Brand: {kw}")
                            pass
                        elif self._is_stop_word(kw):
                             # print(f"   ⚠️ Removed Stop Word: {kw}")
                             pass
                        else:
                            temp_final.append(kw)
                    
                    if temp_final:
                        final = temp_final
                        break # Success
                        
                except Exception as e:
                    print(f"   ⚠️ LLM Error: {e}")
                    continue

            # Fallback if all LLM attempts fail
            if not final:
                print("   ⚠️ LLM Failed all attempts. Using Top 10 by logic.")
                # Simple logic fallback
                final = [item["keyword"] for item in keywords_data[:10] if not contains_trademark(item["keyword"]) and not self._is_stop_word(item["keyword"])]
            
            print(f"   [LLM] 최종 선별 ({len(final)}개): {final}")
            return final
            
        except Exception as e:
            print(f"   ⚠️ LLM 큐레이션 중 오류: {e}")
            # Fallback: 상표 안전 키워드에서 상위 10개 반환
            return [item["keyword"] for item in keywords_data[:10]]

    def _is_stop_word(self, keyword: str) -> bool:
        """
        키워드가 불용어(Stop Words)인지 확인합니다.
        
        Args:
            keyword: 검사할 키워드
            
        Returns:
            True if stop word, False otherwise
        """
        kw = keyword.strip()
        kw_nospace = kw.replace(" ", "")
        
        # 1. Check exact match
        if kw in KEYWORD_STOP_WORDS:
            return True
        if kw_nospace in KEYWORD_STOP_WORDS:
            return True
            
        # 2. Check suffix match for specific categories (e.g., ends with "배송")
        #  (단, "로켓배송" 같은건 리스트에 있지만, "빠른배송" 같은 변종 처리를 위함)
        if kw.endswith("배송") or kw.endswith("발송"):
            return True
            
        # 3. Check for specific substring patterns (careful not to over-filter)
        # "1개", "2세트" 등 수량/단위 패턴 체크
        # '개' '세트' 등으로 끝나는 짧은 단어 (숫자+단위 조합)
        if re.match(r'^\d+(개|세트|묶음|박스|팩|통|병|매|장|롤|켤레|족|pcs|ea|set)$', kw_nospace, re.IGNORECASE):
            return True
            
        # 4. Check if keyword *contains* stop words that should never appear (Specific Garbage)
        # e.g., "하트", "랜덤"
        for stop in KEYWORD_STOP_WORDS:
            # "배송" 같은건 포함되어도 "배송비" 처럼 덜 위험할 수 있지만, 
            # "랜덤", "옵션" 등은 포함되면 거의 100% 쓰레기
            if stop in ["랜덤", "랜덤발송", "옵션", "선택", "하트", "별", "쪽", "기본"]:
                 if stop in kw:
                     return True
                     
        return False

    # ============================================================
    # 유틸리티
    # ============================================================

    def _get_naver_header(self, method, uri):
        """네이버 검색광고 API 인증 헤더 생성"""
        timestamp = str(round(time.time() * 1000))
        message = f"{timestamp}.{method}.{uri}"
        secret_key = self.naver_secret_key
        hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
        signature = base64.b64encode(hash.digest()).decode()
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Timestamp": timestamp,
            "X-API-KEY": self.naver_api_key,
            "X-Customer": self.naver_customer_id,
            "X-Signature": signature
        }


if __name__ == "__main__":
    # 테스트
    kp = KeywordProcessor()
    print(kp.process_keywords("스텐 원형 빨래 건조대"))
