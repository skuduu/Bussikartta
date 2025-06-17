from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "fare_rules.py endpoint working"}
