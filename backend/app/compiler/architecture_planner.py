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
            
        # Auth Strategy — broad detection to avoid missing implicit auth
        _AUTH_ENTITY_NAMES = {
            "user", "users", "account", "accounts", "member", "members",
            "customer", "customers", "employee", "employees", "staff",
            "admin", "admins", "person", "persons", "people", "patient",
            "patients", "doctor", "doctors", "client", "clients",
            "subscriber", "subscribers", "profile", "profiles",
        }
        _AUTH_FEATURE_KEYWORDS = {
            "login", "auth", "authentication", "signup", "register",
            "signin", "logout", "session", "password", "credential",
        }
        has_auth = (
            any(e.is_auth_entity for e in ast.entities)
            or any(e.name.lower() in _AUTH_ENTITY_NAMES for e in ast.entities)
            or any(f.name.lower() in _AUTH_FEATURE_KEYWORDS for f in ast.features)
            or bool(ast.roles)  # any role definitions imply auth is needed
        )
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
        has_realtime = any("real-time" in getattr(c, 'description', '').lower() for c in ast.constraints)
        if has_realtime:
            plan.realtime_strategy = "websocket"
            
        plan.recommendations.append(f"Estimated complexity: {plan.estimated_complexity}")
        plan.recommendations.append(f"Recommended DB strategy: {plan.db_strategy}")
        plan.recommendations.append(f"Recommended API pattern: {plan.api_pattern}")
        
        return plan
