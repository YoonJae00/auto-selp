import pytest
import os
import uuid
from src.api.models import User, Job

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Auto-Selp API"}

def test_create_and_get_job(client, db_session, mocker):
    # Mock the Celery task so it doesn't actually run during the API test
    mocker.patch('src.api.routers.jobs.run_excel_processing_job.delay', return_value=True)
    
    # Create a dummy user in the test database
    dummy_user = User(id=uuid.uuid4(), username="testuser_jobs", hashed_password="hashed")
    db_session.add(dummy_user)
    db_session.commit()
    
    # Override the authentication dependency
    from src.api.deps import get_current_user
    from src.api.main import app
    app.dependency_overrides[get_current_user] = lambda: dummy_user

    # Create a dummy excel file
    dummy_file_path = "dummy_test.xlsx"
    with open(dummy_file_path, "wb") as f:
        f.write(b"dummy excel content")

    try:
        with open(dummy_file_path, "rb") as f:
            response = client.post(
                "/api/jobs/",
                files={"file": ("dummy.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                data={
                    "column_mapping": '{"original_product_name": "A"}',
                    "parallel_count": 1,
                    "processing_options": '{"refine_name": false, "keyword": false, "category": false, "coupang": false}'
                }
            )
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        assert response.json()["status"] == "pending"

        # Test get job status
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["id"] == job_id
        assert response.json()["status"] == "pending"
    finally:
        if os.path.exists(dummy_file_path):
            os.remove(dummy_file_path)
        app.dependency_overrides.clear()
