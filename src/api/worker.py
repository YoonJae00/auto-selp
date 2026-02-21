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
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def process_chunk(chunk_id, data_chunk, job_id, user_id, meta_data, pn_prompt, kw_prompt, cat_processor, coupang_processor, llm_provider, processing_options=None, api_keys=None):
    """
    Process a single chunk of data and update progress in the database.
    
    Args:
        chunk_id: Index of this chunk
        data_chunk: List of rows to process
        job_id: Job ID
        user_id: User ID
        meta_data: Job metadata dictionary
        pn_prompt: Product name prompt
        kw_prompt: Keyword prompt
        cat_processor: Category processor instance
        llm_provider: LLM provider instance
    
    Returns:
        List of processed results
    """
    db = SessionLocal()
    try:
        pn_processor = ProductNameProcessor(llm_provider=llm_provider)
        kw_processor = KeywordProcessor(llm_provider=llm_provider, api_keys=api_keys)
        
        results = []
        total_in_chunk = len(data_chunk)
        
        # Update chunk status to processing
        chunks = meta_data.get("chunks", [])
        if chunk_id < len(chunks):
            chunks[chunk_id]["status"] = "processing"
            chunks[chunk_id]["total_rows"] = total_in_chunk
            
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job_meta = dict(job.meta_data) if job.meta_data else {}
                job_meta["chunks"] = chunks
                job.meta_data = job_meta
                db.commit()
        
        if processing_options is None:
            processing_options = {"refine_name": True, "keyword": True, "category": True, "coupang": False}

        for index, item in enumerate(data_chunk):
            # Check if job has been cancelled
            job = db.query(Job).filter(Job.id == job_id).first()
            if job and job.status == "cancelled":
                print(f"Job {job_id} was cancelled by user (chunk {chunk_id})")
                return results
            
            p_name = item.get('product_name', '')
            current_row = item['row_index']
            
            if not p_name.strip():
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
            
            if processing_options.get("refine_name", True):
                 result_item['refined_name'] = refined_name
                 
            if processing_options.get("keyword", True):
                 result_item['keywords'] = keywords
                 
            if processing_options.get("category", True):
                 result_item['category_code'] = category_code

            if processing_options.get("coupang", False):
                 result_item['coupang_category_code'] = coupang_category_code
                 
            results.append(result_item)
            
            # Update chunk progress every 5 rows or at the end
            if (index + 1) % 5 == 0 or index == total_in_chunk - 1:
                progress = int((index + 1) / total_in_chunk * 100)
                
                job = db.query(Job).filter(Job.id == job_id).first()
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
        
        # Mark chunk as completed
        job = db.query(Job).filter(Job.id == job_id).first()
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
        
    finally:
        db.close()


def process_excel_job(job_id: str, user_id: str, file_path: str):
    db = SessionLocal()
    start_time = time.time()
    
    # 1. Fetch existing job metadata first
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        print(f"Job not found: {job_id}")
        db.close()
        return
        
    existing_meta_data = dict(job.meta_data) if job.meta_data else {}
    
    # 2. Update Status -> processing with start time (preserve existing meta_data)
    existing_meta_data["processing_started_at"] = datetime.now().isoformat()
    job.status = "processing"
    job.meta_data = existing_meta_data
    db.commit()

    try:
        # 3. Extract configuration from metadata
        meta_data = existing_meta_data
        column_mapping = meta_data.get("column_mapping", {})
        processing_options = meta_data.get("processing_options", {
            "refine_name": True,
            "keyword": True,
            "category": True,
            "category": True,
            "coupang": False
        })
        parallel_count = meta_data.get("parallel_count", 1)

        # Extract column info
        original_product_col = column_mapping.get("original_product_name")
        refined_product_col = column_mapping.get("refined_product_name")
        keyword_col = column_mapping.get("keyword")
        category_col = column_mapping.get("category")
        coupang_col = column_mapping.get("coupang_category")
        
        if not original_product_col:
            raise ValueError("Original product name column is required in column_mapping")
        
        # Conditional validation
        if processing_options.get("refine_name", True) and not refined_product_col:
            raise ValueError("Refined product name column is required when option is enabled")
        if processing_options.get("keyword", True) and not keyword_col:
            raise ValueError("Keyword column is required when option is enabled")
        if processing_options.get("category", True) and not category_col:
            raise ValueError("Category column is required when option is enabled")
        if processing_options.get("coupang", False) and not coupang_col:
            raise ValueError("Coupang Category column is required when option is enabled")
        
        # 4. Fetch User's Active Prompts
        pn_prompt_db = db.query(Prompt).filter(Prompt.user_id == user_id, Prompt.type == "product_name", Prompt.is_active == True).first()
        pn_prompt = pn_prompt_db.content if pn_prompt_db else None

        kw_prompt_db = db.query(Prompt).filter(Prompt.user_id == user_id, Prompt.type == "keyword", Prompt.is_active == True).first()
        kw_prompt = kw_prompt_db.content if kw_prompt_db else None

        # 5. Get user's LLM provider preference and API key
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        llm_provider_type = "gemini"  # default
        llm_api_key = None
        api_keys = {}
        
        if user_settings:
            preferences = user_settings.preferences or {}
            api_keys = user_settings.api_keys or {}
            
            # Get LLM provider preference
            llm_provider_type = preferences.get("llm_provider", "gemini")
            
            # Get API key based on provider type
            if llm_provider_type == "openai":
                llm_api_key = get_user_api_key(db, user_id, "openai_api_key")
                print(f"[DEBUG] OpenAI API Key 획득: {llm_api_key[:10] if llm_api_key and len(llm_api_key) >= 10 else llm_api_key}... (길이: {len(llm_api_key) if llm_api_key else 0})")
            elif llm_provider_type == "gemini":
                llm_api_key = get_user_api_key(db, user_id, "gemini_api_key")
                print(f"[DEBUG] Gemini API Key 획득: {llm_api_key[:10] if llm_api_key and len(llm_api_key) >= 10 else llm_api_key}... (길이: {len(llm_api_key) if llm_api_key else 0})")
        
        # Create LLM provider instance
        llm_provider = get_llm_provider(provider_type=llm_provider_type, api_key=llm_api_key)
        print(f"Using LLM provider: {llm_provider_type}")

        # 6. Initialize Processors
        excel_handler = ExcelHandler()
        cat_processor = CategoryProcessor(mapping_file_path="naver_category_mapping.xls", api_keys=api_keys)
        
        # Initialize Coupang Processor
        coupang_access_key = get_user_api_key(db, user_id, "coupang_access_key")
        coupang_secret_key = get_user_api_key(db, user_id, "coupang_secret_key")
        coupang_processor = CoupangCategoryProcessor(coupang_access_key, coupang_secret_key)
        
        # 6. Load Data
        data_list = excel_handler.load_excel(
            file_path, 
            product_name_col=original_product_col,
            keyword_col=None
        )
        total_rows = len(data_list)
        
        # Update total_rows in metadata
        meta_data["total_rows"] = total_rows
        job.meta_data = meta_data
        db.commit()
        
        # 7. Split data into chunks
        chunk_size = (total_rows + parallel_count - 1) // parallel_count  # Ceiling division
        chunks_data = []
        for i in range(parallel_count):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_rows)
            if start_idx < total_rows:
                chunks_data.append(data_list[start_idx:end_idx])
            else:
                chunks_data.append([])
        
        # 8. Process chunks in parallel
        all_results = []
        with ThreadPoolExecutor(max_workers=parallel_count) as executor:
            futures = []
            for chunk_id, data_chunk in enumerate(chunks_data):
                if len(data_chunk) > 0:
                    future = executor.submit(
                        process_chunk,
                        chunk_id,
                        data_chunk,
                        job_id,
                        user_id,
                        meta_data,
                        pn_prompt,
                        kw_prompt,
                        cat_processor,
                        coupang_processor,
                        llm_provider,
                        processing_options,
                        api_keys
                    )
                    futures.append((chunk_id, future))
            
            # Wait for all chunks to complete and collect results
            for chunk_id, future in futures:
                try:
                    chunk_results = future.result()
                    all_results.extend(chunk_results)
                    
                    # Update overall progress
                    completed_chunks = sum(1 for _, f in futures if f.done())
                    overall_progress = int((completed_chunks / len(futures)) * 100)
                    
                    job.progress = overall_progress
                    db.commit()
                    
                except Exception as e:
                    print(f"Error processing chunk {chunk_id}: {e}")
                    raise

        # 9. Sort results by row_index to maintain order
        all_results.sort(key=lambda x: x['row_index'])

        # 10. Save Result to Excel
        output_path = excel_handler.save_results(file_path, all_results, column_mapping)

        meta_data["completed_at"] = datetime.now().isoformat()
        job.status = "completed"
        job.progress = 100
        job.output_file_path = output_path
        job.meta_data = meta_data
        db.commit()

    except Exception as e:
        print(f"Job Failed: {e}")
        meta_data["failed_at"] = datetime.now().isoformat()
        job.status = "failed"
        job.error_message = str(e)
        job.meta_data = meta_data
        db.commit()
        
    finally:
        db.close()
