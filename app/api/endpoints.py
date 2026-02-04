from fastapi import APIRouter, HTTPException
from app.services.diagram_service import diagram_service
from app.models.schemas import DiagramResponse, DiagramListResponse

router = APIRouter()

@router.get("/diagrams", response_model=DiagramListResponse)
async def get_list_diagrams(limit: int = 10):
    """
    Lay danh sach so do (Mac dinh lay 10 cai dau tien)
    """
    return await diagram_service.get_all_diagrams(limit)

@router.get("/diagrams/{diagram_id}", response_model=DiagramResponse)
async def get_diagram_detail(diagram_id: str):
    """
    Lay chi tiet 1 so do (Gop tu Mongo + Neo4j + Postgres)
    """
    result = await diagram_service.get_diagram_by_id(diagram_id)
    if not result:
        raise HTTPException(status_code=404, detail="Khong tim thay so do nay")
    return result