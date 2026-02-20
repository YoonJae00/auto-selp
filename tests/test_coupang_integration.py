import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.worker import process_chunk

class TestCoupangIntegration(unittest.TestCase):
    @patch('src.api.worker.get_db')
    def test_process_chunk_with_coupang_option(self, mock_get_db):
        # Mock DB response
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'status': 'processing'}]

        # Mock dependencies
        # Mock dependencies
        chunk_id = 0
        data_chunk = [{'row_index': 0, 'product_name': 'Test Product'}]
        job_id = 'test_job'
        user_id = 'test_user'
        meta_data = {
            'original_filename': 'test.xlsx',
            'column_mapping': {
                'original_product_name': 'original_name',
                'refined_product_name': 'refined_name',
                'keyword': 'keywords',
                'category': 'category_code',
                'coupang_category': 'coupang_category_code'
            }
        }
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
            chunk_id, data_chunk, job_id, user_id, meta_data,
            pn_prompt, kw_prompt, cat_processor, coupang_processor, llm_provider,
            processing_options=processing_options_enabled
        )
        
        # Verify Coupang processor was called
        coupang_processor.get_category_code.assert_called_with('Refined Name')
        # Verify result contains coupang_category_code
        self.assertIn('coupang_category_code', results_enabled[0])
        self.assertEqual(results_enabled[0]['coupang_category_code'], 'COUPANG_123')

        # 2. Test with Coupang DISABLED
        processing_options_disabled = {
            "refine_name": True,
            "keyword": True,
            "category": True,
            "coupang": False
        }
        
        coupang_processor.reset_mock()
        
        results_disabled = process_chunk(
            chunk_id, data_chunk, job_id, user_id, meta_data,
            pn_prompt, kw_prompt, cat_processor, coupang_processor, llm_provider,
            processing_options=processing_options_disabled
        )
        
        # Verify Coupang processor was NOT called
        coupang_processor.get_category_code.assert_not_called()
        # Verify result does NOT contain coupang_category_code
        self.assertNotIn('coupang_category_code', results_disabled[0])

if __name__ == '__main__':
    unittest.main()
