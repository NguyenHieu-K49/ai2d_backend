from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.diagram_service import diagram_service
from app.models.schemas import DiagramResponse, DiagramListResponse

router = APIRouter()

@router.get("/diagrams", response_model=DiagramListResponse)
async def get_list_diagrams(
    limit: int = 10,
    category: Optional[str] = Query(None, description="Loc theo chu de: foodChainsWebs, lifeCycles, photosynthesisRespiration")
):
    """
    Lay danh sach so do.
    - limit: So luong (mac dinh 10)
    - category: (Tuy chon) Loc theo chu de
    """
    return await diagram_service.get_all_diagrams(limit=limit, category=category)

@router.get("/diagrams/{diagram_id}", response_model=DiagramResponse)
async def get_diagram_detail(diagram_id: str):
    """
    Lay chi tiet 1 so do
    """
    result = await diagram_service.get_diagram_by_id(diagram_id)
    if not result:
        raise HTTPException(status_code=404, detail="Khong tim thay so do nay")
    return result


@router.get("/search/related", response_model=DiagramListResponse)
async def search_related_nodes(
        keyword: str,
        category: Optional[str] = Query(None, description="Loc theo category hien tai")
):
    """
    Tim cac so do lien quan.
    - keyword: Tu khoa (VD: Frog)
    - category: Neu truyen vao, chi tim trong cung chu de (VD: dang xem lifeCycles thi chi tim lifeCycles)
    """
    if not keyword:
        return DiagramListResponse(total=0, items=[])
    return await diagram_service.get_related_diagrams(keyword, current_category=category)