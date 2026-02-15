from src.api.database import get_db
from src.excel_handler import ExcelHandler
from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def process_chunk(chunk_id, data_chunk, job_id, user_id, meta_data, pn_prompt, kw_prompt, cat_processor):
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
    
    Returns:
        List of processed results
    """
    db = get_db()
    pn_processor = ProductNameProcessor()
    kw_processor = KeywordProcessor()
    
    results = []
    total_in_chunk = len(data_chunk)
    
    # Update chunk status to processing
    chunks = meta_data.get("chunks", [])
    if chunk_id < len(chunks):
        chunks[chunk_id]["status"] = "processing"
        chunks[chunk_id]["total_rows"] = total_in_chunk
        
        db.table("jobs").update({
            "meta_data": {
                **meta_data,
                "chunks": chunks
            }
        }).eq("id", job_id).execute()
    
    for index, item in enumerate(data_chunk):
        # Check if job has been cancelled
        job_status_check = db.table("jobs").select("status").eq("id", job_id).execute()
        if job_status_check.data and job_status_check.data[0].get("status") == "cancelled":
            print(f"Job {job_id} was cancelled by user (chunk {chunk_id})")
            return results
        
        p_name = item.get('product_name', '')
        current_row = item['row_index']
        
        # Skip empty rows
        if not p_name.strip():
            continue
        
        # Process product name
        refined_name = pn_processor.refine_product_name(p_name, prompt_template=pn_prompt)
        
        # Process keywords
        keywords = kw_processor.process_keywords(refined_name, prompt_template=kw_prompt)
        
        # Process category
        category_code = cat_processor.get_category_code(refined_name)
        
        # Store result
        results.append({
            'row_index': item['row_index'],
            'refined_name': refined_name,
            'keywords': keywords,
            'category_code': category_code,
            'image_url': ''
        })
        
        # Update chunk progress every 5 rows or at the end
        if (index + 1) % 5 == 0 or index == total_in_chunk - 1:
            progress = int((index + 1) / total_in_chunk * 100)
            
            # Get fresh metadata to avoid overwriting other chunks' updates
            job_res = db.table("jobs").select("meta_data").eq("id", job_id).execute()
            if job_res.data:
                current_meta = job_res.data[0].get("meta_data", {})
                current_chunks = current_meta.get("chunks", [])
                
                if chunk_id < len(current_chunks):
                    current_chunks[chunk_id]["progress"] = progress
                    current_chunks[chunk_id]["rows_processed"] = index + 1
                    current_chunks[chunk_id]["last_updated"] = datetime.now().isoformat()
                    
                    db.table("jobs").update({
                        "meta_data": {
                            **current_meta,
                            "chunks": current_chunks
                        }
                    }).eq("id", job_id).execute()
    
    # Mark chunk as completed
    job_res = db.table("jobs").select("meta_data").eq("id", job_id).execute()
    if job_res.data:
        current_meta = job_res.data[0].get("meta_data", {})
        current_chunks = current_meta.get("chunks", [])
        
        if chunk_id < len(current_chunks):
            current_chunks[chunk_id]["status"] = "completed"
            current_chunks[chunk_id]["progress"] = 100
            
            db.table("jobs").update({
                "meta_data": {
                    **current_meta,
                    "chunks": current_chunks
                }
            }).eq("id", job_id).execute()
    
    return results


def process_excel_job(job_id: str, user_id: str, file_path: str):
    db = get_db()
    start_time = time.time()
    
    # 1. Fetch existing job metadata first
    job_res = db.table("jobs").select("meta_data").eq("id", job_id).execute()
    existing_meta_data = job_res.data[0].get("meta_data", {}) if job_res.data else {}
    
    # 2. Update Status -> processing with start time (preserve existing meta_data)
    db.table("jobs").update({
        "status": "processing",
        "meta_data": {
            **existing_meta_data,
            "processing_started_at": datetime.now().isoformat()
        }
    }).eq("id", job_id).execute()

    try:
        # 3. Extract configuration from metadata
        meta_data = existing_meta_data
        column_mapping = meta_data.get("column_mapping", {})
        parallel_count = meta_data.get("parallel_count", 1)
        
        # Extract column info
        original_product_col = column_mapping.get("original_product_name")
        refined_product_col = column_mapping.get("refined_product_name")
        keyword_col = column_mapping.get("keyword")
        category_col = column_mapping.get("category")
        
        if not original_product_col:
            raise ValueError("Original product name column is required in column_mapping")
        if not refined_product_col:
            raise ValueError("Refined product name column is required in column_mapping")
        if not keyword_col:
            raise ValueError("Keyword column is required in column_mapping")
        if not category_col:
            raise ValueError("Category column is required in column_mapping")
        
        # 4. Fetch User's Active Prompts
        pn_res = db.table("prompts").select("content").eq("user_id", user_id).eq("type", "product_name").eq("is_active", True).execute()
        pn_prompt = pn_res.data[0]['content'] if pn_res.data else None

        kw_res = db.table("prompts").select("content").eq("user_id", user_id).eq("type", "keyword").eq("is_active", True).execute()
        kw_prompt = kw_res.data[0]['content'] if kw_res.data else None

        # 5. Initialize Processors
        excel_handler = ExcelHandler()
        cat_processor = CategoryProcessor(mapping_file_path="naver_category_mapping.xls")
        
        # 6. Load Data
        data_list = excel_handler.load_excel(
            file_path, 
            product_name_col=original_product_col,
            keyword_col=None
        )
        total_rows = len(data_list)
        
        # Update total_rows in metadata
        meta_data["total_rows"] = total_rows
        db.table("jobs").update({
            "meta_data": meta_data
        }).eq("id", job_id).execute()
        
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
                        cat_processor
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
                    
                    db.table("jobs").update({
                        "progress": overall_progress
                    }).eq("id", job_id).execute()
                    
                except Exception as e:
                    print(f"Error processing chunk {chunk_id}: {e}")
                    raise

        # 9. Sort results by row_index to maintain order
        all_results.sort(key=lambda x: x['row_index'])

        # 10. Save Result to Excel
        output_path = excel_handler.save_results(file_path, all_results, column_mapping)

        db.table("jobs").update({
            "status": "completed", 
            "progress": 100, 
            "output_file_path": output_path,
            "meta_data": {
                **meta_data,
                "completed_at": datetime.now().isoformat()
            }
        }).eq("id", job_id).execute()

    except Exception as e:
        print(f"Job Failed: {e}")
        db.table("jobs").update({
            "status": "failed", 
            "error_message": str(e),
            "meta_data": {
                **meta_data,
                "failed_at": datetime.now().isoformat()
            }
        }).eq("id", job_id).execute()
