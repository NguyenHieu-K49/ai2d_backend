from app.core.database import db
from app.core.config import settings
from app.models.schemas import DiagramResponse, GraphStructure, DiagramMeta, GraphNode, GraphEdge, DiagramListResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiagramService:
    async def get_diagram_by_id(self, diagram_id: str):
        # --- 1. MongoDB (Raw BBox) ---
        raw_data = {}
        try:
            mongo_coll = db.get_mongo_db()["diagrams_inventory"]
            item = mongo_coll.find_one({"id": diagram_id})
            if item:
                item.pop("_id", None)
                raw_data = item.get("raw", {})
        except Exception as e:
            logger.error(f"Mongo Error: {e}")

        # --- 2. Neo4j (Graph Structure) ---
        nodes = []
        edges = []
        try:
            # Query cai tien: Lay tat ca Node thuoc Diagram, va tat ca Edge noi giua chung
            query = """
            MATCH (d:Diagram {id: $did})-[:CONTAINS]->(n:Entity)
            OPTIONAL MATCH (n)-[r:LINKED_TO]->(m:Entity)
            WHERE (d)-[:CONTAINS]->(m) 
            RETURN n, r, m
            """
            with db.get_neo4j_session() as session:
                result = session.run(query, did=diagram_id)

                unique_nodes = {}
                unique_edges = set()

                for record in result:
                    # Xu ly Node
                    n_node = record["n"]
                    if n_node:
                        props = dict(n_node)
                        labels = list(n_node.labels)
                        # Label thu 2 thuong la type cu the (vd: Organism)
                        main_type = labels[1] if len(labels) > 1 else "Entity"

                        unique_nodes[props["uid"]] = GraphNode(
                            uid=props["uid"],
                            name=props.get("name", ""),
                            type=main_type
                        )

                    # Xu ly Edge (Chi lay khi ca nguon va dich deu ton tai)
                    r_rel = record["r"]
                    m_node = record["m"]

                    if r_rel and m_node:
                        m_props = dict(m_node)
                        edge_key = (props["uid"], m_props["uid"])

                        if edge_key not in unique_edges:
                            edges.append(GraphEdge(
                                source=props["uid"],
                                target=m_props["uid"],
                                relation="LINKED_TO"
                            ))
                            unique_edges.add(edge_key)

                nodes = list(unique_nodes.values())
        except Exception as e:
            logger.error(f"Neo4j Error: {e}")

        # --- 3. PostgreSQL (Description) ---
        description = ""
        category = "unknown"
        pg_conn = None
        try:
            # Lay ket noi tu Pool
            pg_conn = db.get_postgres_conn()
            cursor = pg_conn.cursor()

            cursor.execute(
                "SELECT category, description FROM diagram_captions WHERE diagram_id = %s",
                (diagram_id,)
            )
            row = cursor.fetchone()
            if row:
                category = row[0]
                description = row[1]

            cursor.close()
        except Exception as e:
            logger.error(f"Postgres Error: {e}")
        finally:
            # Tra ket noi ve Pool (QUAN TRONG)
            if pg_conn:
                db.put_postgres_conn(pg_conn)

        # Neu khong co data o ca 2 nguon chinh thi tra ve None
        if not raw_data and not nodes:
            return None

        # --- 4. Format URL & Response ---
        # Format: .../ai2d/raw/{id}
        final_image_url = f"{settings.R2_BASE_URL}/ai2d/raw/{diagram_id}"

        return DiagramResponse(
            id=diagram_id,
            meta=DiagramMeta(category=category, description=description),
            graph=GraphStructure(nodes=nodes, edges=edges),
            image_url=final_image_url,
            raw_data=raw_data
        )

    async def get_all_diagrams(self, limit=10, category=None):
        diagrams = []
        pg_conn = None
        try:
            pg_conn = db.get_postgres_conn()
            cursor = pg_conn.cursor()

            # Loc theo category
            if category:
                query = "SELECT diagram_id FROM diagram_captions WHERE category = %s LIMIT %s"
                cursor.execute(query, (category, limit))
            else:
                query = "SELECT diagram_id FROM diagram_captions LIMIT %s"
                cursor.execute(query, (limit,))

            rows = cursor.fetchall()
            cursor.close()

            # Loop qua tung ID de lay full data
            for row in rows:
                d_id = row[0]
                detail = await self.get_diagram_by_id(d_id)
                if detail:
                    diagrams.append(detail)

        except Exception as e:
            logger.error(f"List Error: {e}")
        finally:
            if pg_conn:
                db.put_postgres_conn(pg_conn)

        return DiagramListResponse(total=len(diagrams), items=diagrams)

    async def get_related_diagrams(self, keyword: str, current_category: str = None):
        related_diagrams = []
        try:
            #1: Tim ID tu Neo4j
            query = """
            MATCH (d:Diagram)-[:CONTAINS]->(n:Entity)
            WHERE toLower(n.name) CONTAINS toLower($kw)
            RETURN DISTINCT d.id as diagram_id
            """

            with db.get_neo4j_session() as session:
                result = session.run(query, kw=keyword)
                diagram_ids = [record["diagram_id"] for record in result]

            if diagram_ids:
                pg_conn = db.get_postgres_conn()
                cursor = pg_conn.cursor()

                #2: Loc category ngay tai SQL (Postgres)
                # Neu co current_category -> Them dieu kien AND category = ...
                if current_category:
                    sql = """
                    SELECT diagram_id, category, description
                    FROM diagram_captions
                    WHERE diagram_id = ANY (%s) \
                    AND category = %s \
                    """
                    cursor.execute(sql, (diagram_ids, current_category))
                else:
                    # Neu khong co category -> Lay het
                    sql = """
                    SELECT diagram_id, category, description
                    FROM diagram_captions
                    WHERE diagram_id = ANY (%s) \
                    """
                    cursor.execute(sql, (diagram_ids,))

                rows = cursor.fetchall()
                cursor.close()
                db.put_postgres_conn(pg_conn)

                for row in rows:
                    d_id = row[0]
                    related_diagrams.append({
                        "id": d_id,
                        "image_url": f"{settings.R2_BASE_URL}/ai2d/raw/{d_id}",
                        "meta": {
                            "category": row[1],
                            "description": row[2][:100] + "..." if row[2] else ""
                        }
                    })
        except Exception as e:
            logger.error(f"Related Search Error: {e}")
        return DiagramListResponse(total=len(related_diagrams), items=related_diagrams)

diagram_service = DiagramService()