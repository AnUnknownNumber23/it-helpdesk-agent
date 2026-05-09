from fastapi import APIRouter # 导入APIRouter类，用于定义API路由


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
