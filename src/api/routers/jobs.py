import shutil
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from src.api.deps import get_current_user, get_db
from src.api.worker import process_excel_job # Will be implemented

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    # 1. Save File Locally
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Create Job in DB
    db = get_db()
    job_data = {
        "user_id": user.id,
        "input_file_path": file_path,
        "status": "pending",
        "progress": 0,
        "meta_data": {"original_filename": file.filename}
    }
    res = db.table("jobs").insert(job_data).execute()
    job_id = res.data[0]['id']

    # 3. Trigger Background Task
    background_tasks.add_task(process_excel_job, job_id, user.id, file_path)

    return {"job_id": job_id, "status": "pending"}

@router.get("/{job_id}")
def get_job_status(job_id: str, user = Depends(get_current_user)):
    db = get_db()
    res = db.table("jobs").select("*").eq("id", job_id).eq("user_id", user.id).execute()
    if not res.data:
        return {"error": "Job not found"}
    return res.data[0]
