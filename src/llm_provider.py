"""
LLM Provider 추상화 레이어
다양한 LLM 제공자(Gemini, OpenAI)를 통합하여 사용할 수 있도록 추상화
"""

from abc import ABC, abstractmethod
from typing import Optional
import os
import google.generativeai as genai


class BaseLLMProvider(ABC):
    """LLM 제공자 추상 베이스 클래스"""
    
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        """
        주어진 프롬프트로 컨텐츠를 생성합니다.
        
        Args:
            prompt: 생성할 컨텐츠의 프롬프트
            
        Returns:
            생성된 텍스트
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        API 키가 설정되어 있는지 확인합니다.
        
        Returns:
            설정 여부
        """
        pass


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM 제공자"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Gemini Provider를 초기화합니다.
        
        Args:
            api_key: Gemini API 키 (None이면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None
            print("[WARNING] GEMINI_API_KEY not found")
    
    def generate_content(self, prompt: str) -> str:
        """Gemini로 컨텐츠를 생성합니다."""
        if not self.is_configured():
            raise ValueError("Gemini API key is not configured")
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini 컨텐츠 생성 중 오류: {e}")
    
    def is_configured(self) -> bool:
        """Gemini API 키가 설정되어 있는지 확인합니다."""
        return self.api_key is not None and self.model is not None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI ChatGPT LLM 제공자"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        OpenAI Provider를 초기화합니다.
        
        Args:
            api_key: OpenAI API 키 (None이면 환경변수에서 로드)
            model: 사용할 모델 (기본값: gpt-4o-mini)
        """
        raw_api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_key = self._sanitize_api_key(raw_api_key)
        self.model_name = model
        
        if not self.api_key:
            print("[WARNING] OPENAI_API_KEY not found")
        
        # OpenAI 클라이언트는 lazy import로 처리 (설치되지 않았을 수 있음)
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                import httpx
                
                # Custom HTTP client with enforced UTF-8 headers
                http_client = httpx.Client(
                    headers={"Content-Type": "application/json; charset=utf-8"},
                    timeout=60.0
                )
                
                self.client = OpenAI(
                    api_key=self.api_key,
                    http_client=http_client
                )
            except ImportError:
                print("[ERROR] openai 또는 httpx 패키지가 설치되지 않았습니다. pip install openai httpx를 실행하세요.")

    def _sanitize_api_key(self, key: Optional[str]) -> Optional[str]:
        """API 키에서 비-ASCII 문자를 제거하고 유효성을 검증합니다."""
        if not key:
            return None
            
        try:
            # 먼저 user-visible whitespace 제거
            clean_key = key.strip()
            
            # ASCII로 인코딩 가능한지 확인
            clean_key.encode('ascii')
            return clean_key
        except UnicodeEncodeError:
            print(f"[WARNING] API Key에 비-ASCII 문자가 포함되어 있습니다. 정제를 시도합니다.")
            print(f"[DEBUG] 원본 키 일부: {key[:5]}... (길이: {len(key)})")
            
            # 비-ASCII 문자 제거
            cleaned = ''.join(char for char in key if ord(char) < 128).strip()
            
            if not cleaned:
                print("[ERROR] API Key 정제 실패: 유효한 ASCII 문자가 없습니다.")
                return None
                
            print(f"[INFO] API Key 정제 완료. (원본 길이: {len(key)} -> 정제 후: {len(cleaned)})")
            return cleaned
    
    def generate_content(self, prompt: str) -> str:
        """OpenAI로 컨텐츠를 생성합니다."""
        if not self.is_configured():
            raise ValueError("OpenAI API key is not configured")
        
        try:
            # 프롬프트가 문자열인지 확인하고 UTF-8로 안전하게 처리
            if isinstance(prompt, bytes):
                prompt = prompt.decode('utf-8')
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except UnicodeEncodeError as e:
            import traceback
            print(f"[ERROR] 인코딩 오류 상세:")
            print(traceback.format_exc())
            print(f"[DEBUG] 프롬프트 타입: {type(prompt)}, 길이: {len(prompt)}")
            raise Exception(f"OpenAI 컨텐츠 생성 중 인코딩 오류: {e}")
        except Exception as e:
            import traceback
            print(f"[ERROR] OpenAI API 호출 실패:")
            print(traceback.format_exc())
            raise Exception(f"OpenAI 컨텐츠 생성 중 오류: {e}")
    
    def is_configured(self) -> bool:
        """OpenAI API 키가 설정되어 있는지 확인합니다."""
        return self.api_key is not None and self.client is not None


def get_llm_provider(
    provider_type: str = "gemini",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMProvider:
    """
    LLM 제공자 인스턴스를 생성하는 팩토리 함수
    
    Args:
        provider_type: 제공자 타입 ("gemini" 또는 "openai")
        api_key: API 키 (None이면 환경변수 사용)
        model: 사용할 모델 (OpenAI 전용, None이면 기본값 사용)
        
    Returns:
        BaseLLMProvider 인스턴스
        
    Raises:
        ValueError: 지원하지 않는 제공자 타입인 경우
    """
    provider_type = provider_type.lower()
    
    if provider_type == "gemini":
        return GeminiProvider(api_key=api_key)
    elif provider_type == "openai":
        return OpenAIProvider(api_key=api_key, model=model or "gpt-4o-mini")
    else:
        raise ValueError(f"지원하지 않는 LLM 제공자: {provider_type}")


if __name__ == "__main__":
    # 테스트
    print("=== Gemini Provider 테스트 ===")
    try:
        gemini = get_llm_provider("gemini")
        if gemini.is_configured():
            result = gemini.generate_content("안녕하세요를 영어로 번역해주세요.")
            print(f"결과: {result}")
        else:
            print("Gemini API 키가 설정되지 않았습니다.")
    except Exception as e:
        print(f"오류: {e}")
    
    print("\n=== OpenAI Provider 테스트 ===")
    try:
        openai = get_llm_provider("openai")
        if openai.is_configured():
            result = openai.generate_content("안녕하세요를 영어로 번역해주세요.")
            print(f"결과: {result}")
        else:
            print("OpenAI API 키가 설정되지 않았습니다.")
    except Exception as e:
        print(f"오류: {e}")
