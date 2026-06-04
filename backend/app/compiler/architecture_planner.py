from app.schemas.ast_models import RequirementAST, ArchitecturePlan

class ArchitecturePlanner:
    """
    Makes architectural decisions based on the enriched AST.
    """

    def plan(self, ast: RequirementAST) -> ArchitecturePlan:
        plan = ArchitecturePlan()
        
        num_entities = len(ast.entities)
        
        # Complexity Estimation
        if num_entities < 3:
            plan.estimated_complexity = "simple"
            plan.db_strategy = "normalized"
        elif num_entities <= 7:
            plan.estimated_complexity = "medium"
            plan.db_strategy = "normalized"
        elif num_entities <= 15:
            plan.estimated_complexity = "complex"
            plan.db_strategy = "normalized"
            plan.caching_strategy = "redis"
        else:
            plan.estimated_complexity = "enterprise"
            plan.db_strategy = "normalized"
            plan.caching_strategy = "redis"
            plan.search_strategy = "elasticsearch"
            
        # Auth Strategy
        has_auth = any(e.is_auth_entity for e in ast.entities) or any(t.value == "login" for t in (t for node in ast.features for t in node.source_tokens) if hasattr(node, 'source_tokens'))
        if has_auth:
            plan.auth_strategy = "jwt"
        else:
            plan.auth_strategy = "none"
            
        # API Pattern
        plan.api_pattern = "rest"  # Defaulting to REST for now
        
        # File Storage
        has_file_uploads = any(f.field_type in {"file", "image"} for e in ast.entities for f in e.fields)
        if has_file_uploads:
            plan.file_storage = "s3"
            
        # Realtime
        has_realtime = any("real-time" in [t.value for t in getattr(c, 'source_tokens', [])] for c in ast.constraints)
        if has_realtime:
            plan.realtime_strategy = "websocket"
            
        plan.recommendations.append(f"Estimated complexity: {plan.estimated_complexity}")
        plan.recommendations.append(f"Recommended DB strategy: {plan.db_strategy}")
        plan.recommendations.append(f"Recommended API pattern: {plan.api_pattern}")
        
        return plan
