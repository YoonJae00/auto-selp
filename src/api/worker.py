from src.api.database import get_db
from src.excel_handler import ExcelHandler
from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor
import os

async def process_excel_job(job_id: str, user_id: str, file_path: str):
    db = get_db()
    
    # 1. Update Status -> processing
    db.table("jobs").update({"status": "processing"}).eq("id", job_id).execute()

    try:
        # 2. Fetch User's Active Prompts
        # Product Name Prompt
        pn_res = db.table("prompts").select("content").eq("user_id", user_id).eq("type", "product_name").eq("is_active", True).execute()
        pn_prompt = pn_res.data[0]['content'] if pn_res.data else None

        # Keyword Prompt
        kw_res = db.table("prompts").select("content").eq("user_id", user_id).eq("type", "keyword").eq("is_active", True).execute()
        kw_prompt = kw_res.data[0]['content'] if kw_res.data else None

        # 3. Initialize Processors
        excel_handler = ExcelHandler()
        pn_processor = ProductNameProcessor()
        kw_processor = KeywordProcessor()
        # CategoryProcessor doesn't use prompts currently
        
        # 4. Load Data
        df = excel_handler.load_excel(file_path)
        total_rows = len(df)
        
        # TODO: Column mapping should be dynamic from meta_data
        # For now assuming 'PID', 'ProductName' exist or using defaults
        
        # 5. Process Loop
        results = []
        for index, row in df.iterrows():
            # Dummy logic for example - replace with actaul column names
            p_name = str(row.get('상품명', ''))
            
            # (A) Product Name
            new_name = pn_processor.refine_product_name(p_name, prompt_template=pn_prompt)
            
            # (B) Keywords
            keywords = kw_processor.process_keywords(new_name, prompt_template=kw_prompt)

            # Update Progress (every 10%)
            if index % max(1, total_rows // 10) == 0:
                progress = int((index + 1) / total_rows * 100)
                db.table("jobs").update({"progress": progress}).eq("id", job_id).execute()

        # 6. Save Result
        # ... logic to save df to new excel ...
        output_path = file_path.replace(".xlsx", "_result.xlsx")
        # excel_handler.save_excel(df, output_path) # Need to implement save logic in handler to return path

        db.table("jobs").update({
            "status": "completed", 
            "progress": 100, 
            "output_file_path": output_path
        }).eq("id", job_id).execute()

    except Exception as e:
        print(f"Job Failed: {e}")
        db.table("jobs").update({
            "status": "failed", 
            "error_message": str(e)
        }).eq("id", job_id).execute()
