import shutil
import os
import uuid
import json
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.api.deps import get_current_user, get_db
from src.api.models import User, Job
from src.tasks import run_excel_processing_job
from src.excel_handler import ExcelHandler

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    parallel_count: int = Form(1),  # Number of parallel workers (1-10)
    processing_options: str = Form(None), # JSON string, optional
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    엑셀 파일을 업로드하고 처리 작업을 시작합니다.
    
    Args:
        file: 엑셀 파일
        column_mapping: JSON 문자열 형식의 열 매핑 정보
        parallel_count: 병렬 처리 작업 수 (1-10, 기본값: 1)
        processing_options: 처리 옵션 (JSON 문자열)
    """
    # Validate parallel_count
    if parallel_count < 1 or parallel_count > 10:
        raise HTTPException(status_code=400, detail="parallel_count must be between 1 and 10")
    
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
        
    # Parse processing_options
    options = {}
    if processing_options:
        try:
            options = json.loads(processing_options)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid processing_options JSON format")
    
    # Validate required fields based on options
    # Default options if not provided
    if not options:
        options = {
            "refine_name": True,
            "keyword": True,
            "category": True,
            "coupang": False 
        }

    if options.get("refine_name", True) and not mapping.get("refined_product_name"):
        raise HTTPException(status_code=400, detail="Refined product name column is required")
    if options.get("keyword", True) and not mapping.get("keyword"):
        raise HTTPException(status_code=400, detail="Keyword column is required")
    if options.get("category", True) and not mapping.get("category"):
        raise HTTPException(status_code=400, detail="Category column is required")
    if options.get("coupang", False) and not mapping.get("coupang_category"):
        raise HTTPException(status_code=400, detail="Coupang Category column is required")
    
    if not mapping.get("original_product_name"):
        raise HTTPException(status_code=400, detail="Original product name column is required")

    # 3. Initialize chunks metadata
    chunks = [
        {
            "id": i,
            "status": "pending",
            "progress": 0,
            "rows_processed": 0,
            "total_rows": 0
        }
        for i in range(parallel_count)
    ]

    # 4. Create Job in DB
    job_db = Job(
        user_id=user.id,
        input_file_path=file_path,
        status="pending",
        progress=0,
        meta_data={
            "original_filename": file.filename,
            "column_mapping": mapping,
            "parallel_count": parallel_count,
            "processing_options": options,
            "chunks": chunks
        }
    )
    db.add(job_db)
    db.commit()
    db.refresh(job_db)
    job_id = str(job_db.id)

    # 5. Submit job to Celery queue (non-blocking)
    run_excel_processing_job.delay(job_id, str(user.id), file_path)

    return {"job_id": job_id, "status": "pending"}

@router.get("/")
def list_jobs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    사용자의 모든 작업 목록을 조회합니다 (최신순).
    """
    jobs = db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).all()
    # ORM 객체를 dict 로 변환하여 리턴 (Pydantic 모델을 쓰는게 베스트이나 일단 딕셔너리로 호환성 유지)
    return [{
        "id": str(j.id),
        "user_id": str(j.user_id),
        "status": j.status,
        "input_file_path": j.input_file_path,
        "output_file_path": j.output_file_path,
        "progress": j.progress,
        "error_message": j.error_message,
        "meta_data": j.meta_data,
        "created_at": j.created_at.isoformat() if j.created_at else None,
        "updated_at": j.updated_at.isoformat() if j.updated_at else None
    } for j in jobs]

@router.get("/{job_id}")
def get_job_status(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        return {"error": "Job not found"}
    return {
        "id": str(job.id),
        "user_id": str(job.user_id),
        "status": job.status,
        "input_file_path": job.input_file_path,
        "output_file_path": job.output_file_path,
        "progress": job.progress,
        "error_message": job.error_message,
        "meta_data": job.meta_data,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None
    }

@router.get("/{job_id}/download/result")
def download_result(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """처리된 결과 파일을 다운로드합니다."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    output_path = job.output_file_path
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    original_filename = job.meta_data.get('original_filename', 'result.xlsx') if job.meta_data else 'result.xlsx'
    result_filename = f"processed_{original_filename}"
    
    return FileResponse(
        path=output_path,
        filename=result_filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/{job_id}/download/original")
def download_original(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """원본 파일을 다운로드합니다."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    input_path = job.input_file_path
    
    if not input_path or not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Original file not found")
    
    original_filename = job.meta_data.get('original_filename', 'original.xlsx') if job.meta_data else 'original.xlsx'
    
    return FileResponse(
        path=input_path,
        filename=original_filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.delete("/{job_id}/cancel")
def cancel_job(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    진행 중인 작업을 취소합니다.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Only allow cancelling pending or processing jobs
    if job.status not in ['pending', 'processing']:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Update job status to cancelled with timestamp
    from datetime import datetime
    meta_data = dict(job.meta_data) if job.meta_data else {}
    meta_data["cancelled_at"] = datetime.now().isoformat()
    
    job.status = "cancelled"
    job.error_message = "User cancelled the job"
    job.meta_data = meta_data
    db.commit()
    
    return {"message": "Job cancelled successfully", "job_id": job_id}

