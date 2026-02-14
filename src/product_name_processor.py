import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class ProductNameProcessor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("[WARNING] GEMINI_API_KEY not found in .env")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')

    def refine_product_name(self, original_name: str, prompt_template: str = None) -> str:
        """
        Gemini를 사용하여 상품명을 정제합니다.
        - 브랜드 제거
        - 수량/단위 표준화 (10p -> 10개, 1p -> 제거)
        - 검색 최적화
        """
        if not self.api_key:
            return original_name + " (API키 없음)"

        try:

            # 기본 프롬프트 템플릿 (System Default)
            if not prompt_template:
                prompt_template = """
                역할: 전문 온라인 쇼핑몰 MD
                작업: 다음 도매 상품명을 소비자가 검색하기 좋고 깔끔한 '판매용 상품명'으로 변경.
                
                규칙:
                1. '시즈맥스', '3M', '다이소' 같은 **브랜드/제조사 이름은 무조건 제거**.
                2. 불필요한 특수문자([], (), -, /, +) 제거하고 띄어쓰기로 대체.
                3. 수량 표기 표준화:
                   - '1p', '1개', '1set' 처럼 1개 단위는 **표기 삭제**. (예: '수세미 1p' -> '수세미')
                   - 2개 이상은 'N개'로 통일. (예: '10p', '10pset' -> '10개')
                4. 오타 수정 및 문맥에 맞는 자연스러운 단어 배치.
                5. 핵심 키워드는 유지하되, 너무 긴 문장은 핵심 위주로 요약.
                6. 결과물은 **상품명 텍스트만** 출력 (설명 금지).

                원본 상품명: "{{product_name}}"
                가공된 상품명:
                """

            # 템플릿 변수 치환
            prompt = prompt_template.replace("{{product_name}}", original_name)
            
            response = self.model.generate_content(prompt)
            cleaned_name = response.text.strip()
            # 혹시 모를 따옴표 제거
            cleaned_name = cleaned_name.replace('"', '').replace("'", "")
            return cleaned_name

        except Exception as e:
            print(f"상품명 가공 중 오류 발생: {e}")
            return original_name
