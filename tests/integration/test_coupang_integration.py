import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.excel_processing_service import process_chunk

class TestCoupangIntegration(unittest.TestCase):
    @patch('src.services.excel_processing_service.SessionLocal')
    @patch('src.services.excel_processing_service.uuid.UUID')
    def test_process_chunk_with_coupang_option(self, mock_uuid, mock_session_local):
        # Mock DB session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock Job query
        mock_job = MagicMock()
        mock_job.status = "processing"
        mock_job.meta_data = {"chunks": [{"status": "pending"}]}
        mock_db.query.return_value.filter.return_value.first.return_value = mock_job

        # Mock dependencies
        chunk_id = 0
        data_chunk = [{'row_index': 0, 'product_name': 'Test Product'}]
        job_id = 'test_job'
        user_id = 'test_user'
        pn_prompt = "Refine prompt"
        kw_prompt = "Keyword prompt"
        
        # Mock processors
        cat_processor = MagicMock()
        cat_processor.get_category_code.return_value = '123456'
        
        coupang_processor = MagicMock()
        coupang_processor.get_category_code.return_value = 'COUPANG_123'
        
        llm_provider = MagicMock()
        # Mock generate_content which is used by processors
        llm_provider.generate_content.side_effect = ['Refined Name', 'Key, Word']
        llm_provider.is_configured.return_value = True

        # 1. Test with Coupang ENABLED
        processing_options_enabled = {
            "refine_name": True,
            "keyword": True,
            "category": True,
            "coupang": True
        }
        
        results_enabled = process_chunk(
            chunk_id, data_chunk, job_id, user_id,
            pn_prompt, kw_prompt, cat_processor, coupang_processor, llm_provider,
            processing_options=processing_options_enabled,
            api_keys={}
        )
        
        # Verify Coupang processor was called
        coupang_processor.get_category_code.assert_called_with('Refined Name')
        # Verify result contains coupang_category_code
        self.assertIn('coupang_category_code', results_enabled[0])
        self.assertEqual(results_enabled[0]['coupang_category_code'], 'COUPANG_123')

    @patch('src.services.excel_processing_service.SessionLocal')
    @patch('src.services.excel_processing_service.uuid.UUID')
    def test_process_chunk_without_coupang_option(self, mock_uuid, mock_session_local):
        # Mock DB session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock Job query
        mock_job = MagicMock()
        mock_job.status = "processing"
        mock_job.meta_data = {"chunks": [{"status": "pending"}]}
        mock_db.query.return_value.filter.return_value.first.return_value = mock_job

        # Mock dependencies
        chunk_id = 0
        data_chunk = [{'row_index': 0, 'product_name': 'Test Product'}]
        job_id = 'test_job'
        user_id = 'test_user'
        pn_prompt = "Refine prompt"
        kw_prompt = "Keyword prompt"
        
        # Mock processors
        cat_processor = MagicMock()
        cat_processor.get_category_code.return_value = '123456'
        
        coupang_processor = MagicMock()
        
        llm_provider = MagicMock()
        llm_provider.generate_content.side_effect = ['Refined Name', 'Key, Word']
        llm_provider.is_configured.return_value = True

        # 2. Test with Coupang DISABLED
        processing_options_disabled = {
            "refine_name": True,
            "keyword": True,
            "category": True,
            "coupang": False
        }
        
        coupang_processor.reset_mock()
        
        results_disabled = process_chunk(
            chunk_id, data_chunk, job_id, user_id,
            pn_prompt, kw_prompt, cat_processor, coupang_processor, llm_provider,
            processing_options=processing_options_disabled,
            api_keys={}
        )
        
        # Verify Coupang processor was NOT called
        coupang_processor.get_category_code.assert_not_called()
        # Verify result does NOT contain coupang_category_code
        self.assertNotIn('coupang_category_code', results_disabled[0])

if __name__ == '__main__':
    unittest.main()
