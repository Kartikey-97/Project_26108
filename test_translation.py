import asyncio
from dotenv import load_dotenv
load_dotenv("/Users/kartikeygupta/Desktop/sih_26108/backend/.env")

from backend.kartikey.translation.bhashini_client import bhashini_client

async def test():
    text = "The control gear must be safe as per IS 15885."
    print(f"Original (English): {text}")
    
    tamil = await bhashini_client.translate(text, "English", "Tamil")
    print(f"Translated (Tamil): {tamil}")
    
    hindi = await bhashini_client.translate(text, "English", "Hindi")
    print(f"Translated (Hindi): {hindi}")

if __name__ == "__main__":
    asyncio.run(test())
