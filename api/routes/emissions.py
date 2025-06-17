from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "emissions.py endpoint working"}
