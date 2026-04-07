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

def process_chunk(chunk_id, data_chunk, job_id, user_id, meta_data, pn_prompt, kw_prompt, cat_processor, coupang_processor, llm_provider, processing_options=None, api_keys=None):
    """
    Process a single chunk of data and update progress in the database.
    """
    db = SessionLocal()
    results = []
    try:
        # 1. Initialize local processors
        pn_processor = ProductNameProcessor(llm_provider=llm_provider)
        kw_processor = KeywordProcessor(llm_provider=llm_provider, api_keys=api_keys)
        
        total_in_chunk = len(data_chunk)
        if total_in_chunk == 0:
            return []
        
        # 2. Update chunk status to processing
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if job:
            job_meta = dict(job.meta_data) if job.meta_data else {}
            current_chunks = job_meta.get("chunks", [])
            if chunk_id < len(current_chunks):
                current_chunks[chunk_id]["status"] = "processing"
                current_chunks[chunk_id]["total_rows"] = total_in_chunk
                job_meta["chunks"] = current_chunks
                job.meta_data = job_meta
                db.commit()
        
        if processing_options is None:
            processing_options = {"refine_name": True, "keyword": True, "category": True, "coupang": False}

        # 3. Processing loop
        for index, item in enumerate(data_chunk):
            try:
                # Check cancellation
                db.refresh(job)
                if job and job.status == "cancelled":
                    print(f"[PROCESS] Job {job_id} cancelled by user (chunk {chunk_id})")
                    return results
                
                p_name = item.get('product_name', '')
                if not p_name or not p_name.strip():
                    continue
                
                refined_name = p_name
                if processing_options.get("refine_name", True):
                    refined_name = pn_processor.refine_product_name(p_name, prompt_template=pn_prompt)
                
                keywords = ""
                if processing_options.get("keyword", True):
                    keywords = kw_processor.process_keywords(refined_name, prompt_template=kw_prompt)
                
                category_code = ""
                if processing_options.get("category", True):
                    category_code = cat_processor.get_category_code(refined_name)

                coupang_category_code = ""
                if processing_options.get("coupang", False) and coupang_processor:
                    coupang_category_code = coupang_processor.get_category_code(refined_name)
                
                result_item = {
                    'row_index': item['row_index'],
                    'image_url': ''
                }
                
                if processing_options.get("refine_name", True): result_item['refined_name'] = refined_name
                if processing_options.get("keyword", True): result_item['keywords'] = keywords
                if processing_options.get("category", True): result_item['category_code'] = category_code
                if processing_options.get("coupang", False): result_item['coupang_category_code'] = coupang_category_code
                
                results.append(result_item)
                
                # Progress update logic
                if (index + 1) % 5 == 0 or index == total_in_chunk - 1:
                    progress = int((index + 1) / total_in_chunk * 100)
                    job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
                    if job and job.meta_data:
                        current_meta = dict(job.meta_data)
                        current_chunks = current_meta.get("chunks", [])
                        if chunk_id < len(current_chunks):
                            current_chunks[chunk_id]["progress"] = progress
                            current_chunks[chunk_id]["rows_processed"] = index + 1
                            current_chunks[chunk_id]["last_updated"] = datetime.now().isoformat()
                            current_meta["chunks"] = current_chunks
                            job.meta_data = current_meta
                            db.commit()
            except Exception as row_error:
                print(f"[ERROR] Chunk {chunk_id}, Row {item.get('row_index')} failed: {row_error}")
                continue # Keep processing other rows
        
        # 4. Mark chunk as completed
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if job and job.meta_data:
            current_meta = dict(job.meta_data)
            current_chunks = current_meta.get("chunks", [])
            if chunk_id < len(current_chunks):
                current_chunks[chunk_id]["status"] = "completed"
                current_chunks[chunk_id]["progress"] = 100
                current_meta["chunks"] = current_chunks
                job.meta_data = current_meta
                db.commit()
        
        return results
    except Exception as e:
        print(f"[CRITICAL] Chunk {chunk_id} failed: {e}")
        # Update chunk status to failed
        try:
            job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
            if job:
                job_meta = dict(job.meta_data) if job.meta_data else {}
                current_chunks = job_meta.get("chunks", [])
                if chunk_id < len(current_chunks):
                    current_chunks[chunk_id]["status"] = "failed"
                    current_chunks[chunk_id]["error"] = str(e)
                    job.meta_data = job_meta
                    db.commit()
        except: pass
        return results
    finally:
        db.close()


def process_excel_job(job_id: str, user_id: str, file_path: str):
    db = SessionLocal()
    try:
        # 1. Start processing
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if not job:
            print(f"[ERROR] Job not found: {job_id}")
            return
            
        meta_data = dict(job.meta_data) if job.meta_data else {}
        meta_data["processing_started_at"] = datetime.now().isoformat()
        job.status = "processing"
        job.progress = 0
        job.meta_data = meta_data
        db.commit()

        # 2. Extract configuration
        column_mapping = meta_data.get("column_mapping", {})
        processing_options = meta_data.get("processing_options", {"refine_name": True, "keyword": True, "category": True, "coupang": False})
        parallel_count = max(1, meta_data.get("parallel_count", 1))

        # 3. Fetch User Environment & API Keys
        pn_prompt = db.query(Prompt).filter(Prompt.user_id == uuid.UUID(user_id), Prompt.type == "product_name", Prompt.is_active == True).first()
        pn_prompt_content = pn_prompt.content if pn_prompt else None

        kw_prompt = db.query(Prompt).filter(Prompt.user_id == uuid.UUID(user_id), Prompt.type == "keyword", Prompt.is_active == True).first()
        kw_prompt_content = kw_prompt.content if kw_prompt else None

        user_settings = db.query(UserSettings).filter(UserSettings.user_id == uuid.UUID(user_id)).first()
        llm_provider_type = "gemini"
        llm_api_key = None
        api_keys = {}
        
        if user_settings:
            api_keys = user_settings.api_keys or {}
            llm_provider_type = (user_settings.preferences or {}).get("llm_provider", "gemini")
            llm_api_key = get_user_api_key(db, user_id, f"{llm_provider_type}_api_key")
        
        llm_provider = get_llm_provider(provider_type=llm_provider_type, api_key=llm_api_key)

        # 4. Processors Setup
        excel_handler = ExcelHandler()
        cat_processor = CategoryProcessor(mapping_file_path="naver_category_mapping.xls", api_keys=api_keys)
        coupang_access_key = get_user_api_key(db, user_id, "coupang_access_key")
        coupang_secret_key = get_user_api_key(db, user_id, "coupang_secret_key")
        coupang_processor = CoupangCategoryProcessor(coupang_access_key, coupang_secret_key)
        
        # 5. Load & Split Data
        data_list = excel_handler.load_excel(file_path, product_name_col=column_mapping.get("original_product_name"), keyword_col=None)
        total_rows = len(data_list)
        if total_rows == 0:
            raise ValueError("No data found in the excel file.")

        meta_data["total_rows"] = total_rows
        job.meta_data = meta_data
        db.commit()
        
        chunk_size = (total_rows + parallel_count - 1) // parallel_count
        chunks_data = [data_list[i * chunk_size : (i + 1) * chunk_size] for i in range(parallel_count)]
        
        # 6. Parallel Execution
        all_results = []
        with ThreadPoolExecutor(max_workers=parallel_count) as executor:
            futures = {
                executor.submit(
                    process_chunk, i, chunks_data[i], job_id, user_id, meta_data, 
                    pn_prompt_content, kw_prompt_content, cat_processor, coupang_processor, 
                    llm_provider, processing_options, api_keys
                ): i for i in range(len(chunks_data)) if chunks_data[i]
            }
            
            for future in as_completed(futures):
                chunk_id = futures[future]
                try:
                    chunk_results = future.result()
                    all_results.extend(chunk_results)
                    
                    # Overall progress update
                    completed_chunks = sum(1 for f in futures if f.done())
                    job.progress = int((completed_chunks / len(futures)) * 100)
                    db.commit()
                except Exception as e:
                    print(f"[ERROR] Chunk {chunk_id} processing exception: {e}")
                    # Even if one chunk fails, we record the error and continue to mark job as done/failed later

        # 7. Finalize & Save
        if not all_results:
            raise ValueError("All processing attempts failed or no results produced.")

        all_results.sort(key=lambda x: x['row_index'])
        output_path = excel_handler.save_results(file_path, all_results, column_mapping)

        meta_data["completed_at"] = datetime.now().isoformat()
        job.status = "completed"
        job.progress = 100
        job.output_file_path = output_path
        job.meta_data = meta_data
        db.commit()

    except Exception as e:
        print(f"[CRITICAL] Job {job_id} failed: {e}")
        try:
            db.rollback()
            # Ensure status is 'failed' so loading screen doesn't spin forever
            job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
            if job:
                current_meta = dict(job.meta_data) if job.meta_data else {}
                current_meta["failed_at"] = datetime.now().isoformat()
                job.status = "failed"
                job.error_message = str(e)
                job.meta_data = current_meta
                db.commit()
        except Exception as db_error:
            print(f"[CRITICAL] Failed to update job status to FAILED: {db_error}")
    finally:
        db.close()
