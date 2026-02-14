from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.api.deps import get_current_user, get_db

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

class PromptCreate(BaseModel):
    type: str # 'product_name' or 'keyword'
    title: str
    content: str

class PromptResponse(PromptCreate):
    id: str
    user_id: str
    is_active: bool

@router.post("/", response_model=PromptResponse)
def create_prompt(prompt: PromptCreate, user = Depends(get_current_user)):
    db = get_db()
    data = {
        "user_id": user.id,
        "type": prompt.type,
        "title": prompt.title,
        "content": prompt.content,
        "is_active": False # Default
    }
    res = db.table("prompts").insert(data).execute()
    return res.data[0]

@router.get("/", response_model=List[PromptResponse])
def list_prompts(type: Optional[str] = None, user = Depends(get_current_user)):
    db = get_db()
    query = db.table("prompts").select("*").eq("user_id", user.id)
    if type:
        query = query.eq("type", type)
    res = query.execute()
    return res.data

@router.put("/{prompt_id}/active")
def activate_prompt(prompt_id: str, user = Depends(get_current_user)):
    db = get_db()
    
    # 1. Get prompt type
    prompt_res = db.table("prompts").select("type").eq("id", prompt_id).eq("user_id", user.id).execute()
    if not prompt_res.data:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompt_type = prompt_res.data[0]['type']

    # 2. Deactivate all of this type for this user
    db.table("prompts").update({"is_active": False}).eq("user_id", user.id).eq("type", prompt_type).execute()

    # 3. Activate target prompt
    res = db.table("prompts").update({"is_active": True}).eq("id", prompt_id).execute()
    return res.data[0]
