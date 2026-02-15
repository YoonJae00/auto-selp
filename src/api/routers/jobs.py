import shutil
import os
import uuid
import json
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import FileResponse
from src.api.deps import get_current_user, get_db
from src.api.worker import process_excel_job
from src.excel_handler import ExcelHandler

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Thread pool for background jobs
executor = ThreadPoolExecutor(max_workers=4)  # Run up to 4 jobs concurrently

@router.post("/preview")
def preview_excel(
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    """
    엑셀 파일의 첫 5행을 미리보기로 반환합니다.
    
    응답 형식:
    {
        "columns": ["A", "B", "C", ...],
        "headers": ["상품코드", "상품명", "가격", ...],
        "preview_rows": [["P001", "청소용 수세미", "1000", ...], ...]
    }
    """
    # 임시 파일로 저장
    temp_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{temp_id}{ext}")
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # ExcelHandler로 미리보기 생성
        excel_handler = ExcelHandler()
        preview_data = excel_handler.get_preview(temp_path, num_rows=6)  # 헤더 + 5행
        
        return preview_data
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 처리 중 오류 발생: {str(e)}")
    
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/")
def create_job(
    file: UploadFile = File(...),
    column_mapping: str = Form(...),  # JSON string
    user = Depends(get_current_user)
):
    """
    엑셀 파일을 업로드하고 처리 작업을 시작합니다.
    
    Args:
        file: 엑셀 파일
        column_mapping: JSON 문자열 형식의 열 매핑 정보
            예: {
                "original_product_name": "A", 
                "refined_product_name": "B",
                "keyword": "E", 
                "category": "F"
            }
    """
    # 1. Save File Locally
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Parse column mapping
    try:
        mapping = json.loads(column_mapping)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid column_mapping JSON format")
    
    # Validate required fields
    required_fields = ["original_product_name", "refined_product_name", "keyword", "category"]
    for field in required_fields:
        if field not in mapping or not mapping[field]:
            raise HTTPException(status_code=400, detail=f"{field} column is required")

    # 3. Create Job in DB
    db = get_db()
    job_data = {
        "user_id": user.id,
        "input_file_path": file_path,
        "status": "pending",
        "progress": 0,
        "meta_data": {
            "original_filename": file.filename,
            "column_mapping": mapping
        }
    }
    res = db.table("jobs").insert(job_data).execute()
    job_id = res.data[0]['id']

    # 4. Submit job to thread pool (non-blocking)
    executor.submit(process_excel_job, job_id, user.id, file_path)

    return {"job_id": job_id, "status": "pending"}

@router.get("/")
def list_jobs(user = Depends(get_current_user)):
    """
    사용자의 모든 작업 목록을 조회합니다 (최신순).
    """
    db = get_db()
    res = db.table("jobs").select("*").eq("user_id", user.id).order("created_at", desc=True).execute()
    return res.data

@router.get("/{job_id}")
def get_job_status(job_id: str, user = Depends(get_current_user)):
    db = get_db()
    res = db.table("jobs").select("*").eq("id", job_id).eq("user_id", user.id).execute()
    if not res.data:
        return {"error": "Job not found"}
    return res.data[0]

@router.get("/{job_id}/download/result")
def download_result(job_id: str, user = Depends(get_current_user)):
    """처리된 결과 파일을 다운로드합니다."""
    db = get_db()
    job = db.table("jobs").select("*").eq("id", job_id).eq("user_id", user.id).execute()
    
    if not job.data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job.data[0]
    
    if job_data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    output_path = job_data.get('output_file_path')
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    original_filename = job_data.get('meta_data', {}).get('original_filename', 'result.xlsx')
    result_filename = f"processed_{original_filename}"
    
    return FileResponse(
        path=output_path,
        filename=result_filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/{job_id}/download/original")
def download_original(job_id: str, user = Depends(get_current_user)):
    """원본 파일을 다운로드합니다."""
    db = get_db()
    job = db.table("jobs").select("*").eq("id", job_id).eq("user_id", user.id).execute()
    
    if not job.data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job.data[0]
    input_path = job_data.get('input_file_path')
    
    if not input_path or not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Original file not found")
    
    original_filename = job_data.get('meta_data', {}).get('original_filename', 'original.xlsx')
    
    return FileResponse(
        path=input_path,
        filename=original_filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.delete("/{job_id}/cancel")
def cancel_job(job_id: str, user = Depends(get_current_user)):
    """
    진행 중인 작업을 취소합니다.
    """
    db = get_db()
    
    # Get job
    job_res = db.table("jobs").select("*").eq("id", job_id).eq("user_id", user.id).execute()
    if not job_res.data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_res.data[0]
    
    # Only allow cancelling pending or processing jobs
    if job['status'] not in ['pending', 'processing']:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel job with status: {job['status']}"
        )
    
    # Update job status to cancelled with timestamp
    from datetime import datetime
    meta_data = job.get('meta_data', {})
    
    db.table("jobs").update({
        "status": "cancelled",
        "error_message": "User cancelled the job",
        "meta_data": {
            **meta_data,
            "cancelled_at": datetime.now().isoformat()
        }
    }).eq("id", job_id).execute()
    
    return {"message": "Job cancelled successfully", "job_id": job_id}

