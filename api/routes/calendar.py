from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "calendar.py endpoint working"}
