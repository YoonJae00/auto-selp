import pandas as pd
from openpyxl.utils.cell import column_index_from_string
import os

class ExcelHandler:
    def __init__(self):
        pass

    def load_excel(self, file_path: str, product_name_col: str, keyword_col: str = None) -> list:
        """
        엑셀 파일을 읽어와서 처리할 데이터 리스트를 반환합니다.
        
        Args:
            file_path: 엑셀 파일 경로
            product_name_col: 상품명이 있는 열 문자 (예: 'A')
            keyword_col: (옵션) 기존 키워드가 있는 열 문자 (예: 'E')
            
        Returns:
            List[Dict]: [{'row_index': 2, 'product_name': '...', 'input_keyword': '...'}, ...]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        # 열 문자를 인덱스로 변환 (0-based for pandas iloc)
        try:
            p_col_idx = column_index_from_string(product_name_col) - 1
            k_col_idx = (column_index_from_string(keyword_col) - 1) if keyword_col else None
        except ValueError:
            raise ValueError("올바르지 않은 열 문자입니다. (예: 'A', 'AB')")

        df = pd.read_excel(file_path, header=None) # 헤더 없이 읽어서 0행부터 처리 (또는 사용자가 지정?)
        # 보통 1행은 헤더이므로 2행(Index 1)부터 데이터라고 가정.
        # 하지만 pandas는 header=0(기본값)이면 1행을 헤더로 씀.
        # 여기서는 header=0으로 읽고 처리하는게 안전.
        
        df = pd.read_excel(file_path, header=0)
        
        data_list = []
        for idx, row in df.iterrows():
            # row index는 0부터 시작하지만 엑셀 행번호는 header(1행) + 1 + idx + 1 = idx + 2
            excel_row_num = idx + 2
            
            # iloc을 사용하여 열 인덱스로 접근
            p_name = str(row.iloc[p_col_idx]) if pd.notna(row.iloc[p_col_idx]) else ""
            k_word = ""
            if k_col_idx is not None:
                k_word = str(row.iloc[k_col_idx]) if pd.notna(row.iloc[k_col_idx]) else ""
                
            data_list.append({
                'row_index': excel_row_num,
                'product_name': p_name,
                'input_keyword': k_word
            })
            
        return data_list

    def save_results(self, file_path: str, results: list, start_col: str = 'H'):
        """
        결과를 원본 엑셀 파일에 '추가'하여 저장합니다.
        (pandas 대신 openpyxl을 사용하여 기존 서식 유지하며 쓰기)
        """
        from openpyxl import load_workbook
        
        wb = load_workbook(file_path)
        ws = wb.active
        
        start_col_idx = column_index_from_string(start_col)
        
        # 헤더 추가
        headers = ["가공된 상품명", "추천 키워드", "카테고리 코드", "이미지 URL"]
        for i, header in enumerate(headers):
            ws.cell(row=1, column=start_col_idx + i, value=header)
            
        # 데이터 쓰기
        for item in results:
            row_idx = item['row_index']
            ws.cell(row=row_idx, column=start_col_idx, value=item.get('refined_name', ''))
            ws.cell(row=row_idx, column=start_col_idx + 1, value=item.get('keywords', ''))
            ws.cell(row=row_idx, column=start_col_idx + 2, value=item.get('category_code', ''))
            ws.cell(row=row_idx, column=start_col_idx + 3, value=item.get('image_url', ''))
            
        # 저장 (파일명 변경하여 원본 보존)
        new_path = file_path.replace(".xlsx", "_processed.xlsx")
        wb.save(new_path)
        print(f"결과 파일 저장 완료: {new_path}")
        return new_path
