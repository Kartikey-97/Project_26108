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
        self.client = None
        self.model_name = "gemini-3.6-flash"

    def _get_client(self):
        if self.client is None:
            from shared.config import settings
            api_key = settings.google_api_key
            self.client = genai.Client(api_key=api_key)
        return self.client

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translates text from source_lang to target_lang.
        Accepts language names (e.g., 'English', 'Tamil') or codes ('en', 'ta').
        """
        if not text or not text.strip():
            return ""
        
        # Lazy check for API key before calling
        from shared.config import settings
        if not settings.google_api_key:
            logger.warning("BhashiniAdapter: GOOGLE_API_KEY is not set. Skipping translation.")
            return text
            
        prompt = f"""
        You are a highly accurate translation engine representing Bhashini.
        Translate the following text from {source_lang} to {target_lang}.
        Provide ONLY the translated text. Do not include any conversational filler, quotes, or markdown formatting.
        Ensure technical and procurement terms are translated accurately.
        
        Text to translate:
        {text}
        """
        
        try:
            client = self._get_client()
            # We use asyncio.to_thread to keep the async pipeline non-blocking
            response = await asyncio.to_thread(
                client.models.generate_content,
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
