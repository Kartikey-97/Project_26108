import asyncio
import httpx
import sys
sys.path.append("backend")
from kartikey.api.main import app, on_startup
import json

async def test():
    await on_startup()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/procurement/analyze", json={
            "raw_text": "Procurement of Medium and High Tensile Structural Steel for Railway Bridge Construction. The structural steel shall conform strictly to IS 2062. The steel plates should be hot rolled and have a minimum yield strength of 250 MPa. Impact testing at sub-zero temperatures is required for high-altitude deployment. The manufacturer must possess a valid BIS license for the specified grade.",
            "category_hint": "Infrastructure",
            "input_type": "text"
        })
        print(response.status_code)
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text)

asyncio.run(test())
