from celery import shared_task
from src.services.excel_processing_service import process_excel_job
from src.api.database import SessionLocal
from src.api.models import Job
import traceback
import uuid
from datetime import datetime

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
        
        # Last resort error recording in DB if service layer failed to catch it
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
            if job and job.status != "failed":
                job.status = "failed"
                job.error_message = f"Task error: {error_msg}"
                meta = dict(job.meta_data) if job.meta_data else {}
                meta["failed_at"] = datetime.now().isoformat()
                job.meta_data = meta
                db.commit()
        except:
            pass
        finally:
            db.close()
            
        traceback.print_exc()
        raise e
