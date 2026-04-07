import pytest
import uuid
from src.api.models import User, Job
from src.services.excel_processing_service import process_excel_job

def test_job_failure_handling(db_session, mocker):
    # 1. Create a dummy user and job
    user_id = uuid.uuid4()
    job_id = uuid.uuid4()
    
    dummy_user = User(id=user_id, username="error_test_user", hashed_password="hashed")
    db_session.add(dummy_user)
    
    # Initial job state: pending
    dummy_job = Job(
        id=job_id, 
        user_id=user_id, 
        status="pending", 
        input_file_path="non_existent.xlsx",
        meta_data={"parallel_count": 1, "column_mapping": {"original_product_name": "A"}}
    )
    db_session.add(dummy_job)
    db_session.commit()

    # 2. Mock ExcelHandler to throw an error
    mocker.patch('src.services.excel_processing_service.ExcelHandler.load_excel', side_effect=Exception("Simulated Load Error"))

    # 3. Run the processing job (which should fail)
    process_excel_job(str(job_id), str(user_id), "non_existent.xlsx")

    # 4. Verify that the job status is updated to 'failed' and error_message is captured
    db_session.refresh(dummy_job)
    assert dummy_job.status == "failed"
    assert "Simulated Load Error" in dummy_job.error_message
    assert "failed_at" in dummy_job.meta_data

def test_job_progress_sync(db_session, mocker):
    user_id = uuid.uuid4()
    job_id = uuid.uuid4()
    
    dummy_user = User(id=user_id, username="progress_test_user", hashed_password="hashed")
    db_session.add(dummy_user)
    
    dummy_job = Job(
        id=job_id, 
        user_id=user_id, 
        status="pending", 
        input_file_path="dummy.xlsx",
        meta_data={
            "parallel_count": 1, 
            "column_mapping": {"original_product_name": "A"},
            "chunks": [{"id": 0, "status": "pending", "progress": 0}]
        }
    )
    db_session.add(dummy_job)
    db_session.commit()

    # Mock components to simulate a successful run of 1 row
    mocker.patch('src.services.excel_processing_service.ExcelHandler.load_excel', return_value=[{'product_name': 'Test', 'row_index': 1}])
    mocker.patch('src.services.excel_processing_service.ProductNameProcessor.refine_product_name', return_value="Refined")
    mocker.patch('src.services.excel_processing_service.KeywordProcessor.process_keywords', return_value="k1, k2")
    mocker.patch('src.services.excel_processing_service.CategoryProcessor.get_category_code', return_value="123")
    mocker.patch('src.services.excel_processing_service.CoupangCategoryProcessor.get_category_code', return_value="456")
    mocker.patch('src.services.excel_processing_service.ExcelHandler.save_results', return_value="output.xlsx")

    process_excel_job(str(job_id), str(user_id), "dummy.xlsx")

    db_session.refresh(dummy_job)
    assert dummy_job.status == "completed"
    assert dummy_job.progress == 100
    assert "completed_at" in dummy_job.meta_data
