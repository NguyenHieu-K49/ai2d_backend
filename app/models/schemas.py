from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- 1. Khuon mau cho Node & Edge (Tu Neo4j) ---
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

# --- 2. Khuon mau cho Metadata (Tu Mongo & Postgres) ---
class DiagramMeta(BaseModel):
    category: str
    domain: str = "Biology"
    description: Optional[str] = None

# --- 3. KHUON MAU TONG HOP (Response tra ve Frontend) ---
class DiagramResponse(BaseModel):
    id: str
    meta: DiagramMeta
    graph: GraphStructure
    image_url: str
    raw_data: Optional[Dict[str, Any]] = None # Bbox tu Mongo

# Khuon mau cho danh sach (Phan trang)
class DiagramListResponse(BaseModel):
    total: int
    items: List[DiagramResponse]