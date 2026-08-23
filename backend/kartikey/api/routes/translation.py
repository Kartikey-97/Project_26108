from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from kartikey.translation.bhashini_client import bhashini_client

router = APIRouter(prefix="/translate", tags=["Translation (Bhashini Adapter)"])

class TranslationRequest(BaseModel):
    text: str = Field(..., description="The text to translate")
    source_lang: str = Field(default="English", description="Source language (e.g., 'English', 'Hindi')")
    target_lang: str = Field(default="Hindi", description="Target language (e.g., 'Tamil', 'Telugu')")

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str

@router.post("/", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    """
    Translates text between Indian languages. 
    Currently routed through the LLM adapter pending Bhashini API approval.
    """
    try:
        result = await bhashini_client.translate(req.text, req.source_lang, req.target_lang)
        return TranslationResponse(
            translated_text=result,
            source_lang=req.source_lang,
            target_lang=req.target_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
