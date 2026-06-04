from collections import defaultdict
from typing import Optional, Any

from app.knowledge_graph.entities import GraphNode, GraphEdge, NodeType, EdgeType
from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema
)

class KnowledgeGraph:
    """
    Custom directed graph with forward/reverse adjacency lists.
    """

    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self._forward: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        self._reverse: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)
        self._forward[edge.source][edge.edge_type.value].append(edge.target)
        self._reverse[edge.target][edge.edge_type.value].append(edge.source)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> list[str]:
        if edge_type:
            return self._forward[node_id].get(edge_type.value, [])
        else:
            neighbors = []
            for targets in self._forward[node_id].values():
                neighbors.extend(targets)
            return neighbors

    def get_sources(self, node_id: str, edge_type: Optional[EdgeType] = None) -> list[str]:
        if edge_type:
            return self._reverse[node_id].get(edge_type.value, [])
        else:
            sources = []
            for src_list in self._reverse[node_id].values():
                sources.extend(src_list)
            return sources

    def find_orphans(self) -> list[GraphNode]:
        orphans = []
        for node_id, node in self.nodes.items():
            if not self.get_sources(node_id) and node.node_type not in {NodeType.ENTITY, NodeType.PAGE}:
                # some nodes naturally have no sources like root pages or main entities, 
                # but endpoints or fields without sources might be orphans
                orphans.append(node)
        return orphans

    def find_missing_permissions(self) -> list[tuple[str, str]]:
        missing = []
        # Find endpoints that require a role but the role does not grant permission to the endpoint's entity
        # Simplified check for demonstration
        return missing

    def detect_cycles(self) -> list[list[str]]:
        # Tarjan's or similar could be implemented here
        return []

    def validate_references(self) -> list[str]:
        errors = []
        for edge in self.edges:
            if edge.source not in self.nodes:
                errors.append(f"Edge source missing: {edge.source}")
            if edge.target not in self.nodes:
                errors.append(f"Edge target missing: {edge.target}")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.model_dump() for n in self.nodes.values()],
            "edges": [e.model_dump() for e in self.edges],
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }

    @classmethod
    def build_from_schemas(cls, 
                           ast: RequirementAST, 
                           ui: UISchema, 
                           api: APISchema, 
                           db: DBSchema, 
                           auth: AuthSchema, 
                           business_logic: BusinessLogicSchema) -> "KnowledgeGraph":
        graph = cls()
        
        # 1. Add AST Entities and Fields
        for entity in ast.entities:
            entity_id = f"entity:{entity.name}"
            graph.add_node(GraphNode(id=entity_id, node_type=NodeType.ENTITY, label=entity.name))
            for field in entity.fields:
                field_id = f"field:{entity.name}.{field.name}"
                graph.add_node(GraphNode(id=field_id, node_type=NodeType.FIELD, label=field.name))
                graph.add_edge(GraphEdge(source=entity_id, target=field_id, edge_type=EdgeType.HAS_FIELD))
        
        # 2. Add API Endpoints
        for endpoint in api.endpoints:
            ep_id = f"endpoint:{endpoint.method}:{endpoint.path}"
            graph.add_node(GraphNode(id=ep_id, node_type=NodeType.ENDPOINT, label=ep_id))
            if endpoint.entity:
                entity_id = f"entity:{endpoint.entity}"
                graph.add_edge(GraphEdge(source=ep_id, target=entity_id, edge_type=EdgeType.REFERENCES))
                
        # 3. Add UI Pages
        for page in ui.pages:
            page_id = f"page:{page.route}"
            graph.add_node(GraphNode(id=page_id, node_type=NodeType.PAGE, label=page.title))
            for ds in page.data_sources:
                # Naive matching of data source (e.g. /api/v1/users) to endpoint
                ep_id = f"endpoint:GET:{ds}"
                graph.add_edge(GraphEdge(source=page_id, target=ep_id, edge_type=EdgeType.CALLS))
                
        # Add roles, DB tables, etc. similarly as needed for deeper validation
        
        return graph
