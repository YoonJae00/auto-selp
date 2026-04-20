from typing import List, Dict, Any, Optional
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from src.api.database import SessionLocal
from src.api.models import Job, UserSettings, Prompt
from src.utils.llm_provider import BaseLLMProvider, get_llm_provider
from src.processors.product_name_processor import ProductNameProcessor
from src.processors.keyword_processor import KeywordProcessor
from src.processors.category_processor import CategoryProcessor
from src.processors.coupang_category_processor import CoupangCategoryProcessor
from src.utils.user_settings_utils import get_user_api_key
from src.utils.excel_handler import ExcelHandler

from .processing_pipeline import ProcessingPipeline
from .stages import ProductNameStage, KeywordStage, CategoryStage

logger = logging.getLogger(__name__)

class ExcelProcessingService:
    """엑셀 처리의 전체 흐름과 DB 상태를 관리하는 오케스트레이터 서비스입니다."""
    
    def __init__(self, db: Session, job_id: str, user_id: str):
        self.db = db
        self.job_id = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
        self.user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        self.job = self._get_job()

    def _get_job(self) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == self.job_id).first()

    def create_pipeline(
        self, 
        llm_provider: BaseLLMProvider, 
        cat_processor: CategoryProcessor,
        coupang_processor: Optional[CoupangCategoryProcessor],
        api_keys: Dict[str, str],
        options: Dict[str, bool],
        pn_prompt: Optional[str],
        kw_prompt: Optional[str]
    ) -> ProcessingPipeline:
        """설정에 맞는 파이프라인을 구성합니다."""
        
        context = {
            "options": options,
            "pn_prompt": pn_prompt,
            "kw_prompt": kw_prompt,
            "api_keys": api_keys
        }
        
        pipeline = ProcessingPipeline(context)
        
        # 각 프로세서 인스턴스 생성 (한 번만 수행됨)
        pn_processor = ProductNameProcessor(llm_provider=llm_provider)
        kw_processor = KeywordProcessor(llm_provider=llm_provider, api_keys=api_keys)
        
        # 파이프라인에 스테이지 등록
        pipeline.add_stage(ProductNameStage(pn_processor))
        pipeline.add_stage(KeywordStage(kw_processor))
        pipeline.add_stage(CategoryStage(cat_processor, coupang_processor))
        
        return pipeline

    def process_rows(self, chunk_id: int, data_chunk: List[Dict], pipeline: ProcessingPipeline) -> List[Dict[str, Any]]:
        """데이터 청크를 파이프라인을 통해 처리하고 DB 상태를 업데이트합니다."""
        results = []
        total_rows = len(data_chunk)
        
        if total_rows == 0:
            return []

        self._init_chunk_meta(chunk_id, total_rows)

        for index, row in enumerate(data_chunk):
            # 취소 여부 확인
            self.db.refresh(self.job)
            if self.job and self.job.status == "cancelled":
                logger.info(f"Job {self.job_id} cancelled during chunk {chunk_id}")
                return results

            try:
                # 파이프라인 실행
                processed_row = pipeline.execute(row)
                results.append(processed_row)
                
                # 주기적 진행률 업데이트 (5행마다 또는 마지막 행)
                if (index + 1) % 5 == 0 or index == total_rows - 1:
                    progress = int((index + 1) / total_rows * 100)
                    self._update_chunk_progress(chunk_id, progress, index + 1)
                    
            except Exception as e:
                logger.error(f"Error processing row index {row.get('row_index')} in chunk {chunk_id}: {e}")

        self._finalize_chunk(chunk_id, "completed")
        return results

    # --- DB 상태 관리 헬퍼 메서드 ---

    def _init_chunk_meta(self, chunk_id: int, total_rows: int):
        if not self.job: return
        meta = dict(self.job.meta_data) if self.job.meta_data else {}
        chunks = meta.get("chunks", [])
        if chunk_id < len(chunks):
            chunks[chunk_id].update({
                "status": "processing", 
                "total_rows": total_rows,
                "start_time": datetime.now().isoformat()
            })
            self.job.meta_data = meta
            self.db.commit()

    def _update_chunk_progress(self, chunk_id: int, progress: int, rows_processed: int):
        if not self.job: return
        meta = dict(self.job.meta_data)
        chunks = meta.get("chunks", [])
        if chunk_id < len(chunks):
            chunks[chunk_id].update({
                "progress": progress, 
                "rows_processed": rows_processed, 
                "last_updated": datetime.now().isoformat()
            })
            self.job.meta_data = meta
            self.db.commit()

    def _finalize_chunk(self, chunk_id: int, status: str, error: Optional[str] = None):
        if not self.job: return
        meta = dict(self.job.meta_data) if self.job.meta_data else {}
        chunks = meta.get("chunks", [])
        if chunk_id < len(chunks):
            chunks[chunk_id]["status"] = status
            if status == "completed":
                chunks[chunk_id]["progress"] = 100
            if error:
                chunks[chunk_id]["error"] = error
            chunks[chunk_id]["end_time"] = datetime.now().isoformat()
            self.job.meta_data = meta
            self.db.commit()

# --- 외부 진입점 함수 (함수 레벨) ---

def process_excel_job(job_id: str, user_id: str, file_path: str):
    """
    엑셀 파일을 읽어 청크별로 파이프라인을 실행하는 전체 작업 진입점입니다.
    """
    db = SessionLocal()
    try:
        service = ExcelProcessingService(db, job_id, user_id)
        job = service.job
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        # 1. 설정 및 리소스 로드
        u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == u_id).first()
        if not user_settings:
            raise Exception("사용자 설정을 찾을 수 없습니다.")

        api_keys = {"openai": get_user_api_key(db, u_id, "openai")}
        llm_provider = get_llm_provider(user_settings.llm_provider or "openai", api_keys)
        
        cat_processor = CategoryProcessor()
        coupang_processor = CoupangCategoryProcessor() if user_settings.use_coupang else None
        
        active_prompts = db.query(Prompt).filter(Prompt.user_id == u_id, Prompt.is_active == True).all()
        pn_prompt = next((p.content for p in active_prompts if p.type == "product_name"), None)
        kw_prompt = next((p.content for p in active_prompts if p.type == "keyword"), None)

        # 2. 엑셀 데이터 로드
        handler = ExcelHandler(file_path)
        column_mapping = job.meta_data.get("column_mapping", {}) if job.meta_data else {}
        data = handler.read_excel(column_mapping)
        
        if not data:
            raise Exception("엑셀 파일에 데이터가 없거나 형식이 잘못되었습니다.")

        # 3. 파이프라인 구성
        options = {
            "refine_name": user_settings.refine_product_name,
            "keyword": user_settings.extract_keywords,
            "category": user_settings.match_category,
            "coupang": user_settings.use_coupang
        }
        pipeline = service.create_pipeline(
            llm_provider, cat_processor, coupang_processor, api_keys, 
            options, pn_prompt, kw_prompt
        )

        # 4. 청크 처리
        chunk_size = 50
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        meta = dict(job.meta_data) if job.meta_data else {}
        meta["total_rows"] = len(data)
        meta["chunks"] = [{"id": i, "status": "pending", "progress": 0} for i in range(len(chunks))]
        job.meta_data = meta
        db.commit()

        all_results = []
        for i, data_chunk in enumerate(chunks):
            chunk_results = service.process_rows(i, data_chunk, pipeline)
            all_results.extend(chunk_results)
            
            job.progress = int((len(all_results) / len(data)) * 100)
            db.commit()

        # 5. 결과 저장
        output_file = file_path.replace(".xlsx", "_processed.xlsx")
        handler.write_excel(all_results, output_file)
        
        job.status = "completed"
        job.progress = 100
        job.output_file_path = output_file
        db.commit()

    except Exception as e:
        logger.error(f"Critical error in job {job_id}: {e}")
        db.rollback()
        # 서비스 내 job 객체를 통해 상태 업데이트 시도
        try:
            job_to_fail = db.query(Job).filter(Job.id == uuid.UUID(job_id) if isinstance(job_id, str) else job_id).first()
            if job_to_fail:
                job_to_fail.status = "failed"
                job_to_fail.error_message = str(e)
                db.commit()
        except: pass
        raise e
    finally:
        db.close()

def process_chunk(chunk_id, data_chunk, job_id, user_id, pn_prompt, kw_prompt, cat_processor, coupang_processor, llm_provider, processing_options, api_keys):
    """레거시 호환용 래퍼 함수"""
    db = SessionLocal()
    try:
        service = ExcelProcessingService(db, job_id, user_id)
        pipeline = service.create_pipeline(
            llm_provider, cat_processor, coupang_processor, api_keys, 
            processing_options, pn_prompt, kw_prompt
        )
        return service.process_rows(chunk_id, data_chunk, pipeline)
    finally:
        db.close()
