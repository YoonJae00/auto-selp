from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from src.api.deps import get_current_user, get_db
from src.api.models import User, Prompt

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

class PromptCreate(BaseModel):
    type: str # 'product_name' or 'keyword'
    title: str
    content: str
    is_active: Optional[bool] = False

class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None

class PromptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    type: str
    title: str
    content: str
    is_active: bool

# ─── 필수 변수 정의 ─────────────────────────────────────────────
REQUIRED_VARIABLES: Dict[str, List[str]] = {
    "product_name": ["{{product_name}}"],
    "keyword": ["{{product_name}}", "{{keywords_str}}"],
}

# ─── 기본 프롬프트 템플릿 ────────────────────────────────────────
DEFAULT_PROMPTS = [
    {
        "type": "product_name",
        "title": "기본 상품명 가공 (Default)",
        "content": """역할: 전문 온라인 쇼핑몰 MD
작업: 다음 도매 상품명을 소비자가 검색하기 좋고 깔끔한 '판매용 상품명'으로 변경.

규칙:
1. '시즈맥스', '3M', '다이소' 같은 **브랜드/제조사 이름은 무조건 제거**.
2. 불필요한 특수문자([], (), -, /, +) 제거하고 띄어쓰기로 대체.
3. 수량 표기 표준화:
   - '1p', '1개', '1set' 처럼 1개 단위는 **표기 삭제**. (예: '수세미 1p' -> '수세미')
   - 2개 이상은 'N개'로 통일. (예: '10p', '10pset' -> '10개')
4. 오타 수정 및 문맥에 맞는 자연스러운 단어 배치.
5. 핵심 키워드는 유지하되, 너무 긴 문장은 핵심 위주로 요약.
6. 결과물은 **상품명 텍스트만** 출력 (설명 금지).

원본 상품명: "{{product_name}}"
가공된 상품명:""",
        "is_active": True
    },
    {
        "type": "keyword",
        "title": "기본 키워드 발굴 (Default)",
        "content": """역할: 스마트스토어/쿠팡 전문 마케터
작업: 주어진 '후보 키워드 리스트'에서 소상공인 셀러가 판매하기 유리한 '알짜배기 키워드' 5~8개를 선별해주세요.

상품명: {{product_name}}

[필수 제거 조건] - 위반 시 절대 안됨
1. **상표권/대형 브랜드** 포함된 키워드 무조건 삭제 (예: 삼성, LG, 다이소, 이케아, 3M, 시즈맥스, 나이키 등).
2. 너무 광범위하고 경쟁이 치열한 '대형 키워드' 삭제 (예: 그냥 '의자', '책상', '수납함' 같은 단일 명사).
3. 상품과 관련 없는 키워드 삭제.

[선호 조건]
1. **세부 키워드(Long-tail)** 우선 (예: '투명 화장품 정리함', '원룸 책상 꾸미기').
2. 구매 전환율이 높을 것 같은 구체적인 키워드.

후보 키워드 리스트: [{{keywords_str}}]

결과 출력 형식:
키워드1, 키워드2, 키워드3, ... (콤마로만 구분하여 출력, 설명 없이)""",
        "is_active": True
    }
]


def validate_template_variables(prompt_type: str, content: str):
    """프롬프트 내용에 필수 템플릿 변수가 포함되어 있는지 검증"""
    required = REQUIRED_VARIABLES.get(prompt_type)
    if not required:
        return  # 알 수 없는 타입은 검증 스킵

    missing = [var for var in required if var not in content]
    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "필수 템플릿 변수가 누락되었습니다.",
                "missing_variables": missing,
                "prompt_type": prompt_type,
            }
        )


# ─── CRUD 엔드포인트 ─────────────────────────────────────────────

@router.post("/", response_model=PromptResponse)
def create_prompt(prompt: PromptCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 템플릿 변수 검증
    validate_template_variables(prompt.type, prompt.content)

    # If setting active=True, deactivate others of same type
    if prompt.is_active:
        db.query(Prompt).filter(Prompt.user_id == user.id, Prompt.type == prompt.type).update({"is_active": False})

    new_prompt = Prompt(
        user_id=user.id,
        type=prompt.type,
        title=prompt.title,
        content=prompt.content,
        is_active=prompt.is_active if prompt.is_active is not None else False
    )
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    # UUID를 string으로 변환해서 반환하기 위해 Pydantic 변환 전 dict로 맞춤
    return {
        "id": str(new_prompt.id),
        "user_id": str(new_prompt.user_id),
        "type": new_prompt.type,
        "title": new_prompt.title,
        "content": new_prompt.content,
        "is_active": new_prompt.is_active
    }

@router.get("/", response_model=List[PromptResponse])
def list_prompts(type: Optional[str] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    # 1. Check if user has ANY prompts (간단한 조회로 확인)
    has_prompts = db.query(Prompt).filter(Prompt.user_id == user.id).first()
    
    if not has_prompts:
        # Seeding logic
        print(f"Seeding default prompts for user {user.id}")
        for p in DEFAULT_PROMPTS:
            new_p = Prompt(
                user_id=user.id,
                type=p["type"],
                title=p["title"],
                content=p["content"],
                is_active=p["is_active"]
            )
            db.add(new_p)
        db.commit()

    # 2. Query prompts
    query = db.query(Prompt).filter(Prompt.user_id == user.id)
    if type:
        query = query.filter(Prompt.type == type)
    
    # Order by created_at desc
    prompts = query.order_by(Prompt.created_at.desc()).all()
    
    return [
        {
            "id": str(p.id),
            "user_id": str(p.user_id),
            "type": p.type,
            "title": p.title,
            "content": p.content,
            "is_active": p.is_active
        } for p in prompts
    ]

@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: str, prompt: PromptUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    # Check ownership
    existing = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.user_id == user.id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    update_data = prompt.dict(exclude_unset=True)
    if not update_data:
        return {
            "id": str(existing.id), "user_id": str(existing.user_id), "type": existing.type,
            "title": existing.title, "content": existing.content, "is_active": existing.is_active
        }

    # 템플릿 변수 검증 (content가 변경되는 경우)
    if "content" in update_data:
        prompt_type = update_data.get("type", existing.type)
        validate_template_variables(prompt_type, update_data["content"])

    for key, value in update_data.items():
        setattr(existing, key, value)
        
    db.commit()
    db.refresh(existing)
    
    return {
        "id": str(existing.id), "user_id": str(existing.user_id), "type": existing.type,
        "title": existing.title, "content": existing.content, "is_active": existing.is_active
    }

@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    # Check ownership
    existing = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.user_id == user.id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Delete
    db.delete(existing)
    db.commit()
    
    return {"message": "Prompt deleted"}

@router.put("/{prompt_id}/active")
def activate_prompt(prompt_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    # 1. Get prompt type
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.user_id == user.id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompt_type = prompt.type

    # 2. Deactivate all of this type for this user
    db.query(Prompt).filter(Prompt.user_id == user.id, Prompt.type == prompt_type).update({"is_active": False})

    # 3. Activate target prompt
    prompt.is_active = True
    db.commit()
    db.refresh(prompt)
    
    return {
        "id": str(prompt.id), "user_id": str(prompt.user_id), "type": prompt.type,
        "title": prompt.title, "content": prompt.content, "is_active": prompt.is_active
    }


# ─── 추가 엔드포인트: 기본값 조회 / 초기화 ──────────────────────

@router.get("/defaults")
def get_default_prompts():
    """기본 프롬프트 템플릿 목록 반환 (로그인 불필요)"""
    return DEFAULT_PROMPTS

@router.put("/{prompt_id}/reset", response_model=PromptResponse)
def reset_prompt_to_default(prompt_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """프롬프트를 기본 템플릿 내용으로 초기화"""

    # 1. Check ownership & get type
    existing = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.user_id == user.id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt_type = existing.type

    # 2. Find matching default
    default = next((d for d in DEFAULT_PROMPTS if d["type"] == prompt_type), None)
    if not default:
        raise HTTPException(status_code=404, detail="해당 타입의 기본 템플릿이 없습니다.")

    # 3. Update to default content
    existing.title = default["title"]
    existing.content = default["content"]
    db.commit()
    db.refresh(existing)

    return {
        "id": str(existing.id), "user_id": str(existing.user_id), "type": existing.type,
        "title": existing.title, "content": existing.content, "is_active": existing.is_active
    }
