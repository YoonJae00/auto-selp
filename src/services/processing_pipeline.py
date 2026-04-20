from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseProcessorStage(ABC):
    """모든 데이터 처리 스테이지의 추상 베이스 클래스입니다."""
    
    @abstractmethod
    def process(self, row: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 한 행을 처리합니다.
        
        Args:
            row: 현재 처리 중인 데이터 행
            context: 모든 스테이지가 공유하는 실행 문맥 (API 키, 옵션 등)
            
        Returns:
            가공된 데이터 행
        """
        pass

class ProcessingPipeline:
    """여러 스테이지를 순차적으로 실행하는 데이터 처리 엔진입니다."""
    
    def __init__(self, context: Dict[str, Any]):
        self.stages: List[BaseProcessorStage] = []
        self.context = context

    def add_stage(self, stage: BaseProcessorStage):
        """파이프라인에 처리 단계를 추가합니다."""
        self.stages.append(stage)
        return self

    def execute(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """등록된 모든 스테이지를 순서대로 실행합니다."""
        current_data = row.copy()
        
        for stage in self.stages:
            try:
                current_data = stage.process(current_data, self.context)
            except Exception as e:
                stage_name = stage.__class__.__name__
                logger.error(f"Error in stage {stage_name}: {e}")
                # 특정 스테이지 실패 시 에러 정보를 행 데이터에 기록하고 계속 진행할지 여부는 전략에 따라 결정
                # 여기서는 에러 메시지를 기록하고 다음 스테이지로 넘깁니다.
                current_data[f"{stage_name}_error"] = str(e)
                
        return current_data
