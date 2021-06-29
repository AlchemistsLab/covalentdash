import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from constants import CHAIN_IDS
import config


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/asset-allocation/{chain_slug}/{wallet_address}/")
async def read_item(wallet_address: str, chain_slug: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.covalenthq.com/v1/{CHAIN_IDS[chain_slug]}/address/{wallet_address}/portfolio_v2/?format=format%3Dcsv&key={config.API_KEY}"  # noqa: E501
        ) as response:
            response_json = await response.json()
            if "items" not in response_json:
                raise HTTPException(status_code=404)
            return response_json
