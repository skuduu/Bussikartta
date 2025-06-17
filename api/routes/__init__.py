from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "__init__.py endpoint working"}
