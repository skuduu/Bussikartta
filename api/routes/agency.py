from fastapi import APIRouter

router = APIRouter()

@router.get("/agency")
def get_agency():
    return {
        "agency_id": "HSL",
        "agency_name": "Helsinki Regional Transport Authority",
        "agency_url": "https://www.hsl.fi/",
        "agency_timezone": "Europe/Helsinki",
        "agency_lang": "fi",
        "agency_phone": "+358 9 4766 4000"
    }