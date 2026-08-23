import logging
import asyncio
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class BhashiniAdapter:
    """
    Adapter for Bhashini Translation API (National Language Translation Mission).
    
    For the MVP presentation, this uses an LLM (Gemini) fallback to ensure 100% 
    uptime and multi-lingual support without waiting for API key approval 
    from the Bhashini dashboard.
    """
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-3.6-flash"

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translates text from source_lang to target_lang.
        Accepts language names (e.g., 'English', 'Tamil') or codes ('en', 'ta').
        """
        if not text or not text.strip():
            return ""
            
        prompt = f"""
        You are a highly accurate translation engine representing Bhashini.
        Translate the following text from {source_lang} to {target_lang}.
        Provide ONLY the translated text. Do not include any conversational filler, quotes, or markdown formatting.
        Ensure technical and procurement terms are translated accurately.
        
        Text to translate:
        {text}
        """
        
        try:
            # We use asyncio.to_thread to keep the async pipeline non-blocking
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Safe fallback: return the original text if translation fails
            return text

# Singleton instance for the app
bhashini_client = BhashiniAdapter()
