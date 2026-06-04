from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema,
    ValidationIssue
)
from app.knowledge_graph.graph import KnowledgeGraph
from app.knowledge_graph.validators import GraphValidator

class ConsistencyEngine:
    """
    Builds the knowledge graph and runs cross-reference validation.
    """

    def check(self, 
              ast: RequirementAST, 
              ui_schema: UISchema, 
              api_schema: APISchema, 
              db_schema: DBSchema, 
              auth_schema: AuthSchema, 
              business_logic: BusinessLogicSchema) -> tuple[KnowledgeGraph, list[ValidationIssue]]:
        
        # 1. Build Knowledge Graph
        graph = KnowledgeGraph.build_from_schemas(ast, ui_schema, api_schema, db_schema, auth_schema, business_logic)
        
        # 2. Validate Graph
        validator = GraphValidator()
        issues = validator.validate(graph)
        
        return graph, issues
