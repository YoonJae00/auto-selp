# Auto-Selp Backend Refactoring Plan

## 1. Understanding Summary
- **Project**: Auto-Selp, a backend API tool for automating bulk shopping mall product uploads from Excel files.
- **Goal**: Refactor the backend to support frequent feature additions safely, specifically stabilizing the background Celery tasks (like the loading screen/progress tracking) which currently have an uncertain status.
- **Audience**: Administrators/Sellers needing automated product metadata generation (name refinement, keywords, category mapping).
- **Key Constraints**: Developed without documentation, making the current state of features hard to verify. Frequent changes cause instability.

## 2. Assumptions
- The file upload and core Excel automation parts (e.g., `excel_handler`, `product_name_processor`) are currently functioning correctly.
- The primary goal is structural stability, bug prevention (via testing), and resolving issues with the background task progress/loading screen, rather than pure performance optimization.
- A test-driven approach is preferred, meaning we will write tests against the existing working code to create a baseline before modifying any architecture.

## 3. Decision Log
| Decision | Alternatives Considered | Rationale |
| :--- | :--- | :--- |
| **Test-Driven Stabilization & Modular Refactoring** | 1. Total Architecture Overhaul (Clean Architecture).<br>2. Documentation-First & Minimal Fixes. | Chosen to provide the safest path forward. Establishing a test baseline prevents regressions during refactoring, while isolating business logic makes frequent feature additions easier. |
| **Pytest with Mocking for Core Processors** | Hitting real LLM endpoints during testing. | Ensures tests run quickly, deterministically, and without consuming API credits (Gemini/OpenAI). |
| **Explicit State Machine for Jobs** | Relying purely on basic boolean flags or implicit status checks. | Essential to fix the hanging loading screen issues. Clear states (`PENDING`, `PROCESSING`, `FAILED`, `COMPLETED`) provide unambiguous feedback to the frontend. |

## 4. Final Design & Execution Plan

### Phase 1: Test Infrastructure Setup
1. Install `pytest`, `pytest-cov`, `pytest-mock`, `httpx`.
2. Configure `pytest.ini` and an in-memory SQLite database for testing (`tests/conftest.py`).
3. Write unit tests for core processors: `product_name_processor.py`, `keyword_processor.py`, `category_processor.py` (mocking LLM calls).
4. Write integration tests for FastAPI endpoints: `/api/jobs/` (file upload) and `/api/jobs/{job_id}` (status polling).

### Phase 2: Celery & State Management Stabilization
1. Introduce robust `try-except` blocks in `src/tasks.py` and `src/api/worker.py` to catch all exceptions during background processing.
2. Update the `Job` model to correctly transition through states (`PENDING` -> `PROCESSING` -> `COMPLETED`/`FAILED`).
3. Ensure that `Job.error_message` is populated upon failure, allowing the frontend loading screen to handle errors gracefully instead of hanging.
4. Synchronize `Job.progress` consistently during Excel chunk processing.

### Phase 3: Modular Decoupling
1. Extract the core logic of `process_excel_job` into a dedicated service layer (e.g., `src/services/excel_processing_service.py`).
2. Ensure the API routers (`src/api/routers/jobs.py`) and Celery tasks (`src/tasks.py`) only act as entry points that call this new service layer, decoupling business logic from web/framework dependencies.
