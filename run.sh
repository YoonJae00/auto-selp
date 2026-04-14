#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function usage() {
    echo "사용법: $0 [dev|test|down]"
    echo "  dev   : 로컬 개발 환경 실행 (Hot Reload 활성화, 8000포트)"
    echo "  test  : 로컬 CI 테스트 실행 (DB/Redis 기동 -> 테스트 -> 전체 삭제)"
    echo "  down  : 실행 중인 모든 로컬 개발 컨테이너 정지 및 리소스 삭제"
    exit 1
}

if [ -z "$1" ]; then
    usage
fi

COMPOSE_FILE="docker-compose.local.yml"

case "$1" in
    dev)
        echo -e "${BLUE}=== 로컬 개발 환경을 시작합니다 (Hot Reload) ===${NC}"
        docker-compose -f $COMPOSE_FILE up --build
        ;;
    test)
        echo -e "${BLUE}=== 로컬 CI 테스트를 시작합니다 ===${NC}"
        # 1. 환경 준비 및 빌드
        docker-compose -f $COMPOSE_FILE build
        
        # 2. DB/Redis 기동 및 Backend에서 pytest 실행
        docker-compose -f $COMPOSE_FILE run --rm backend pytest tests/
        
        TEST_EXIT_CODE=$?
        
        # 3. 정리 (볼륨 및 빌드된 이미지까지 삭제)
        echo -e "${BLUE}=== 테스트 환경 및 이미지 정리 중... ===${NC}"
        docker-compose -f $COMPOSE_FILE down -v --rmi local
        docker image prune -f
        
        if [ $TEST_EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}✔ 모든 테스트가 성공적으로 완료되었습니다!${NC}"
        else
            echo -e "${RED}✘ 일부 테스트가 실패했습니다. 로그를 확인하세요.${NC}"
        fi
        exit $TEST_EXIT_CODE
        ;;
    down)
        echo -e "${BLUE}=== 로컬 리소스 및 이미지 정리 중... ===${NC}"
        docker-compose -f $COMPOSE_FILE down -v --rmi local
        docker image prune -f
        echo -e "${GREEN}✔ 정리 완료.${NC}"
        ;;
    *)
        usage
        ;;
esac
