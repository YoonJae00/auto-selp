from src.api.database import get_db, SessionLocal
from src.api.models import Job, Prompt, UserSettings
from src.excel_handler import ExcelHandler
from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor
from src.coupang_category_processor import CoupangCategoryProcessor
from src.llm_provider import get_llm_provider
from src.user_settings_utils import get_user_api_key
import os
import time
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from typing import List, Dict, Any, Optional
from src.api.database import SessionLocal
from src.api.models import Job, Prompt, UserSettings
from src.excel_handler import ExcelHandler
from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor
from src.coupang_category_processor import CoupangCategoryProcessor
from src.llm_provider import get_llm_provider, BaseLLMProvider
from src.user_settings_utils import get_user_api_key
import os
import time
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from sqlalchemy.orm import Session

def _update_job_status(db: Session, job_id: uuid.UUID, status: str, progress: Optional[int] = None, error_message: Optional[str] = None, meta_updates: Optional[Dict] = None):
    """Internal helper to safely update job status and metadata."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return
    
    if status: job.status = status
    if progress is not None: job.progress = progress
    if error_message is not None: job.error_message = error_message
    
    if meta_updates:
        current_meta = dict(job.meta_data) if job.meta_data else {}
        current_meta.update(meta_updates)
        job.meta_data = current_meta
        
    db.commit()

def process_chunk(
    chunk_id: int, 
    data_chunk: List[Dict], 
    job_id: str, 
    user_id: str, 
    pn_prompt: Optional[str], 
    kw_prompt: Optional[str], 
    cat_processor: CategoryProcessor, 
    coupang_processor: Optional[CoupangCategoryProcessor], 
    llm_provider: BaseLLMProvider, 
    processing_options: Dict[str, bool], 
    api_keys: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Processes a subset of excel rows."""
    db = SessionLocal()
    results = []
    job_uuid = uuid.UUID(job_id)
    
    try:
        pn_processor = ProductNameProcessor(llm_provider=llm_provider)
        kw_processor = KeywordProcessor(llm_provider=llm_provider, api_keys=api_keys)
        
        total_in_chunk = len(data_chunk)
        if total_in_chunk == 0: return []
        
        # Initialize chunk status
        job = db.query(Job).filter(Job.id == job_uuid).first()
        if job:
            meta = dict(job.meta_data) if job.meta_data else {}
            chunks = meta.get("chunks", [])
            if chunk_id < len(chunks):
                chunks[chunk_id].update({"status": "processing", "total_rows": total_in_chunk})
                job.meta_data = meta
                db.commit()

        for index, item in enumerate(data_chunk):
            try:
                db.refresh(job)
                if job and job.status == "cancelled":
                    return results
                
                p_name = item.get('product_name', '').strip()
                if not p_name: continue
                
                row_res = {'row_index': item['row_index'], 'image_url': ''}
                
                # Main Logic Pipeline
                refined_name = p_name
                if processing_options.get("refine_name"):
                    refined_name = pn_processor.refine_product_name(p_name, prompt_template=pn_prompt)
                    row_res['refined_name'] = refined_name
                
                if processing_options.get("keyword"):
                    row_res['keywords'] = kw_processor.process_keywords(refined_name, prompt_template=kw_prompt)
                
                if processing_options.get("category"):
                    row_res['category_code'] = cat_processor.get_category_code(refined_name)

                if processing_options.get("coupang") and coupang_processor:
                    row_res['coupang_category_code'] = coupang_processor.get_category_code(refined_name)
                
                results.append(row_res)
                
                # Periodic Progress Update
                if (index + 1) % 5 == 0 or index == total_in_chunk - 1:
                    _update_chunk_progress(db, job_uuid, chunk_id, int((index + 1) / total_in_chunk * 100), index + 1)
                    
            except Exception as e:
                print(f"[ERROR] Chunk {chunk_id}, Row {item.get('row_index')} failed: {e}")
        
        _finalize_chunk_status(db, job_uuid, chunk_id, "completed")
        return results
    except Exception as e:
        print(f"[CRITICAL] Chunk {chunk_id} system failure: {e}")
        _finalize_chunk_status(db, job_uuid, chunk_id, "failed", str(e))
        return results
    finally:
        db.close()

def _update_chunk_progress(db: Session, job_id: uuid.UUID, chunk_id: int, progress: int, rows: int):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job and job.meta_data:
        meta = dict(job.meta_data)
        chunks = meta.get("chunks", [])
        if chunk_id < len(chunks):
            chunks[chunk_id].update({"progress": progress, "rows_processed": rows, "last_updated": datetime.now().isoformat()})
            job.meta_data = meta
            db.commit()

def _finalize_chunk_status(db: Session, job_id: uuid.UUID, chunk_id: int, status: str, error: Optional[str] = None):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job and job.meta_data:
        meta = dict(job.meta_data)
        chunks = meta.get("chunks", [])
        if chunk_id < len(chunks):
            chunks[chunk_id]["status"] = status
            if status == "completed": chunks[chunk_id]["progress"] = 100
            if error: chunks[chunk_id]["error"] = error
            job.meta_data = meta
            db.commit()

def process_excel_job(job_id: str, user_id: str, file_path: str):
    """Main entry point for processing an excel file via background worker."""
    db = SessionLocal()
    job_uuid = uuid.UUID(job_id)
    user_uuid = uuid.UUID(user_id)
    
    try:
        # 1. Initialize Job
        job = db.query(Job).filter(Job.id == job_uuid).first()
        if not job: return
        
        _update_job_status(db, job_uuid, "processing", progress=0, meta_updates={"processing_started_at": datetime.now().isoformat()})

        # 2. Setup Environment
        meta = dict(job.meta_data)
        options = meta.get("processing_options", {"refine_name": True, "keyword": True, "category": True})
        parallel_count = max(1, meta.get("parallel_count", 1))

        # API Keys & LLM
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_uuid).first()
        provider_type = (settings.preferences or {}).get("llm_provider", "gemini") if settings else "gemini"
        api_key = get_user_api_key(db, user_id, f"{provider_type}_api_key")
        llm_provider = get_llm_provider(provider_type=provider_type, api_key=api_key)
        
        # Processors
        api_keys = settings.api_keys if settings else {}
        excel_handler = ExcelHandler()
        cat_proc = CategoryProcessor(api_keys=api_keys)
        coupang_proc = CoupangCategoryProcessor(get_user_api_key(db, user_id, "coupang_access_key"), get_user_api_key(db, user_id, "coupang_secret_key"))
        
        # Prompts
        pn_p = db.query(Prompt).filter(Prompt.user_id == user_uuid, Prompt.type == "product_name", Prompt.is_active == True).first()
        kw_p = db.query(Prompt).filter(Prompt.user_id == user_uuid, Prompt.type == "keyword", Prompt.is_active == True).first()

        # 3. Load & Process
        data = excel_handler.load_excel(file_path, product_name_col=meta.get("column_mapping", {}).get("original_product_name"))
        if not data: raise ValueError("Excel file is empty or invalid.")
        
        _update_job_status(db, job_uuid, None, meta_updates={"total_rows": len(data)})
        
        # Split & Execute
        size = (len(data) + parallel_count - 1) // parallel_count
        chunks = [data[i * size : (i + 1) * size] for i in range(parallel_count)]
        
        all_results = []
        with ThreadPoolExecutor(max_workers=parallel_count) as executor:
            futures = {
                executor.submit(
                    process_chunk, i, chunks[i], job_id, user_id, 
                    pn_p.content if pn_p else None, kw_p.content if kw_p else None,
                    cat_proc, coupang_proc, llm_provider, options, api_keys
                ): i for i in range(len(chunks)) if chunks[i]
            }
            
            for future in as_completed(futures):
                all_results.extend(future.result())
                completed = sum(1 for f in futures if f.done())
                _update_job_status(db, job_uuid, None, progress=int((completed / len(futures)) * 100))

        if not all_results: raise ValueError("No rows were successfully processed.")

        # 4. Success Finalization
        all_results.sort(key=lambda x: x['row_index'])
        out_path = excel_handler.save_results(file_path, all_results, meta.get("column_mapping", {}))
        _update_job_status(db, job_uuid, "completed", progress=100, meta_updates={"completed_at": datetime.now().isoformat()}, error_message="")
        job.output_file_path = out_path
        db.commit()

    except Exception as e:
        print(f"[CRITICAL] Job {job_id} failure: {e}")
        _update_job_status(db, job_uuid, "failed", error_message=str(e), meta_updates={"failed_at": datetime.now().isoformat()})
    finally:
        db.close()
