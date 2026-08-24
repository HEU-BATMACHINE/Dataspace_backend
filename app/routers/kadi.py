from fastapi import APIRouter
import httpx
import asyncio
import os

router = APIRouter(tags=["kadi"], prefix="/kadi")

PAT = os.getenv("PAT")
BASE_URL = "https://apache/api/v1/records"
HEADERS = {"Authorization": f"Bearer {PAT}"}


@router.get("/records")
async def list_records():
    """Fetch records and return just the list of identifiers"""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(BASE_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        return [
            {"id": item.get("id"), "identifier": item.get("identifier")}
            for item in data.get("items", [])
        ]


@router.get("/records/expanded")
async def list_expanded_records():
    """
    Fetch all records, then expand each one by fetching its details.
    Returns a list of full record objects: [{...}, {...}]
    """
    async with httpx.AsyncClient(verify=False) as client:
        list_response = await client.get(BASE_URL, headers=HEADERS)
        list_response.raise_for_status()
        data = list_response.json()
        items = data.get("items", [])

        async def fetch_detail(item):
            record_id = item.get("id")
            if not record_id:
                return {}
            detail_resp = await client.get(f"{BASE_URL}/{record_id}", headers=HEADERS)
            detail_resp.raise_for_status()
            return detail_resp.json()

        results = await asyncio.gather(*[fetch_detail(item) for item in items])

        return results


@router.get("/records/{record_id}")
async def get_record_details(record_id: str):
    """Fetch a single record by ID"""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"{BASE_URL}/{record_id}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
