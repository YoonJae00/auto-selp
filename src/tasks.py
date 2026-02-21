from celery import shared_task
from src.api.worker import process_excel_job
import traceback

@shared_task(bind=True)
def run_excel_processing_job(self, job_id: str, user_id: str, file_path: str):
    """
    Celery task to run the excel processing pipeline.
    """
    try:
        process_excel_job(job_id=job_id, user_id=user_id, file_path=file_path)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        error_msg = str(e)
        print(f"Error in background task for job {job_id}: {error_msg}")
        traceback.print_exc()
        raise e
