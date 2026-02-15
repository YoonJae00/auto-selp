from src.api.database import get_db
from src.excel_handler import ExcelHandler
from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor
import os
import time
from datetime import datetime, timedelta

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
            **existing_meta_data,  # Preserve column_mapping and other data
            "processing_started_at": datetime.now().isoformat()
        }
    }).eq("id", job_id).execute()

    try:
        # 3. Extract column mapping from existing metadata
        meta_data = existing_meta_data
        column_mapping = meta_data.get("column_mapping", {})

        
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
        
        # 3. Fetch User's Active Prompts
        # Product Name Prompt
        pn_res = db.table("prompts").select("content").eq("user_id", user_id).eq("type", "product_name").eq("is_active", True).execute()
        pn_prompt = pn_res.data[0]['content'] if pn_res.data else None

        # Keyword Prompt
        kw_res = db.table("prompts").select("content").eq("user_id", user_id).eq("type", "keyword").eq("is_active", True).execute()
        kw_prompt = kw_res.data[0]['content'] if kw_res.data else None

        # 4. Initialize Processors
        excel_handler = ExcelHandler()
        pn_processor = ProductNameProcessor()
        kw_processor = KeywordProcessor()
        cat_processor = CategoryProcessor()
        
        # 5. Load Data with dynamic column mapping
        # We only need to READ from original_product_name column
        data_list = excel_handler.load_excel(
            file_path, 
            product_name_col=original_product_col,
            keyword_col=None  # We don't need existing keywords
        )
        total_rows = len(data_list)
        
        # 6. Process Loop
        results = []
        last_step_update = None
        
        for index, item in enumerate(data_list):
            # Check if job has been cancelled
            job_status_check = db.table("jobs").select("status").eq("id", job_id).execute()
            if job_status_check.data and job_status_check.data[0].get("status") == "cancelled":
                print(f"Job {job_id} was cancelled by user")
                return  # Exit gracefully
            
            p_name = item.get('product_name', '')
            input_keyword = item.get('input_keyword', '')
            current_row = item['row_index']
            
            # Skip empty rows
            if not p_name.strip():
                continue
            
            # (A) Product Name Processing
            if last_step_update != 'product_name':
                elapsed_time = time.time() - start_time
                rows_processed = index + 1
                avg_time_per_row = elapsed_time / rows_processed if rows_processed > 0 else 0
                remaining_rows = total_rows - rows_processed
                estimated_seconds = avg_time_per_row * remaining_rows
                
                db.table("jobs").update({
                    "meta_data": {
                        **meta_data,
                        "current_row": current_row,
                        "total_rows": total_rows,
                        "current_step": "product_name",
                        "last_updated": datetime.now().isoformat(),
                        "rows_processed": rows_processed,
                        "estimated_completion_seconds": int(estimated_seconds)
                    }
                }).eq("id", job_id).execute()
                last_step_update = 'product_name'
            
            refined_name = pn_processor.refine_product_name(p_name, prompt_template=pn_prompt)
            
            # (B) Keyword Processing
            if last_step_update != 'keyword':
                elapsed_time = time.time() - start_time
                rows_processed = index + 1
                avg_time_per_row = elapsed_time / rows_processed if rows_processed > 0 else 0
                remaining_rows = total_rows - rows_processed
                estimated_seconds = avg_time_per_row * remaining_rows
                
                db.table("jobs").update({
                    "meta_data": {
                        **meta_data,
                        "current_row": current_row,
                        "total_rows": total_rows,
                        "current_step": "keyword",
                        "last_updated": datetime.now().isoformat(),
                        "rows_processed": rows_processed,
                        "estimated_completion_seconds": int(estimated_seconds)
                    }
                }).eq("id", job_id).execute()
                last_step_update = 'keyword'
            
            keywords = kw_processor.process_keywords(refined_name, prompt_template=kw_prompt)
            
            # (C) Category Processing
            if last_step_update != 'category':
                elapsed_time = time.time() - start_time
                rows_processed = index + 1
                avg_time_per_row = elapsed_time / rows_processed if rows_processed > 0 else 0
                remaining_rows = total_rows - rows_processed
                estimated_seconds = avg_time_per_row * remaining_rows
                
                db.table("jobs").update({
                    "meta_data": {
                        **meta_data,
                        "current_row": current_row,
                        "total_rows": total_rows,
                        "current_step": "category",
                        "last_updated": datetime.now().isoformat(),
                        "rows_processed": rows_processed,
                        "estimated_completion_seconds": int(estimated_seconds)
                    }
                }).eq("id", job_id).execute()
                last_step_update = 'category'
            
            category_code = ""
            # TODO: Implement category processing if category_col is provided
            
            # Store result
            results.append({
                'row_index': item['row_index'],
                'refined_name': refined_name,
                'keywords': keywords,
                'category_code': category_code,
                'image_url': ''  # TODO: Image generation if needed
            })

            # Update Progress (every 10 rows)
            if index % 10 == 0 or index == total_rows - 1:
                progress = int((index + 1) / total_rows * 100)
                elapsed_time = time.time() - start_time
                rows_processed = index + 1
                avg_time_per_row = elapsed_time / rows_processed if rows_processed > 0 else 0
                remaining_rows = total_rows - rows_processed
                estimated_seconds = avg_time_per_row * remaining_rows
                
                db.table("jobs").update({
                    "progress": progress,
                    "meta_data": {
                        **meta_data,
                        "current_row": current_row,
                        "total_rows": total_rows,
                        "rows_processed": rows_processed,
                        "estimated_completion_seconds": int(estimated_seconds),
                        "last_updated": datetime.now().isoformat()
                    }
                }).eq("id", job_id).execute()

        # 7. Save Result to Excel
        output_path = excel_handler.save_results(file_path, results, column_mapping)

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
