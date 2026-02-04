from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Khuon mau cho Node & Edge (Tu Neo4j)
class GraphNode(BaseModel):
    uid: str
    name: str
    type: str = "Entity"

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    via: Optional[str] = None

class GraphStructure(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# Khuon mau cho Metadata (Tu Mongo & Postgres)
class DiagramMeta(BaseModel):
    category: str
    domain: str = "Biology"
    description: Optional[str] = None

# Khuon mau tong hop (Response tra ve Frontend)
class DiagramResponse(BaseModel):
    id: str
    meta: DiagramMeta
    graph: Optional[GraphStructure] = None
    image_url: str
    raw_data: Optional[Dict[str, Any]] = None

# Khuon mau cho danh sach (Phan trang)
class DiagramListResponse(BaseModel):
    total: int
    items: List[DiagramResponse]