# Auto-Selp Project Mandates

이 파일의 지침은 프로젝트 내의 다른 모든 설정보다 우선하며, Gemini CLI 에이전트가 작업을 수행할 때 반드시 준수해야 하는 핵심 원칙입니다.

## 1. 아키텍처 및 기술 스택 원칙
- **DB 우선주의**: 모든 데이터 저장 및 설정 조회는 SQLAlchemy(`src/api/database.py`)를 통해 수행한다. **Supabase SDK 사용은 엄격히 금지한다.**
- **모듈화 구조**: 
    - 비즈니스 로직은 `src/processors/`에 위치한다.
    - 유틸리티는 `src/utils/`에 위치한다.
    - 웹 API는 `src/api/`에 위치하며, 서비스 레이어인 `src/services/`를 통해 로직을 호출한다.
- **암호화**: API 키 등 민감 정보는 반드시 암호화하여 저장하며, 복호화 시 `ENCRYPTION_KEY`를 사용한다.

## 2. 파일 및 경로 규칙
- **데이터 참조**: 엑셀, 매핑 파일 등 정적 데이터는 반드시 `data/` 디렉토리를 기준으로 참조한다. (예: `data/naver_category_mapping.xls`)
- **진입점**:
    - CLI 도구: `cli.py`
    - 백엔드 서버: `src/api/main.py`
- **임포트 경로**: 절대 경로(예: `from src.processors...`)를 선호하며, 구조 변경 시 모든 파일의 임포트를 일관되게 업데이트한다.

## 3. 테스트 및 검증Mandates
- **외부 API 차단**: `pytest` 실행 시 외부 LLM(Gemini, OpenAI) 및 네이버 API 호출은 **반드시 Mocking**해야 한다. 실제 API 호출로 인한 무한 대기나 비용 발생을 방지한다.
- **테스트 분류**:
    - 단위 테스트: `tests/unit/`
    - 통합 테스트: `tests/integration/`
    - 수동/유틸리티: `tests/manual/`
- **회귀 방지**: 코드 변경 후에는 반드시 `pytest tests/unit/`을 실행하여 기존 로직의 정상 작동을 확인한다.

## 4. 환경 변수 필수 체크
- 작업을 시작하기 전 `.env`에 다음 항목이 설정되어 있는지 확인한다:
    - `DATABASE_URL`, `GEMINI_API_KEY`, `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`, `JWT_SECRET_KEY`, `ENCRYPTION_KEY`

---
*이 지침은 2026-04-20에 최종 업데이트되었으며, 프로젝트의 안정성과 일관성을 유지하기 위해 수정 시 반드시 사용자 승인을 거친다.*
