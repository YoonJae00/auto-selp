import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# src 모듈 경로 설정을 위해
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from category_processor import CategoryProcessor

class TestRestoration(unittest.TestCase):
    def test_mapping_restore_and_cache(self):
        """CategoryProcessor가 엑셀 매핑을 사용하고 캐싱하는지 테스트"""
        
        # 1. First Instantiation - Should load from file
        with patch('pandas.read_excel') as mock_read_excel:
            # Mock Excel content
            mock_df = MagicMock()
            mock_df.iterrows.return_value = [
                (0, {'대분류': 'A', '중분류': 'B', '소분류': 'C', '세분류': 'D', '카테고리번호': '12345'})
            ]
            mock_read_excel.return_value = mock_df
            
            # Setup mock existence check
            with patch('os.path.exists', return_value=True):
                # Clear cache first for test isolation
                CategoryProcessor._mapping_cache = {}
                
                print("\n[Test] Creating 1st instance (Should Load)")
                processor1 = CategoryProcessor(mapping_file_path="mock.xls")
                
                # Verify pandas read called
                mock_read_excel.assert_called_once()
                
                # 2. Second Instantiation - Should NOT load from file (Cache Hit)
                print("[Test] Creating 2nd instance (Should Cache Hit)")
                processor2 = CategoryProcessor(mapping_file_path="mock.xls")
                
                # Verify pandas read NOT called again
                mock_read_excel.assert_called_once()
                
                # Verify data shared
                self.assertEqual(processor1.category_mapping, processor2.category_mapping)
                self.assertEqual(processor1.category_mapping.get("A>B>C>D"), "12345")
                print(">> [PASS] Caching verified")

if __name__ == "__main__":
    unittest.main()
