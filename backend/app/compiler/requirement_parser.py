import hashlib
from typing import Optional

from app.schemas.ast_models import (
    RequirementAST,
    Token,
    TokenType,
    EntityNode,
    FeatureNode,
    FeatureType,
    ActionNode,
    ActionVerb,
    RoleNode,
    PlanNode,
    ASTMetadata,
    SourceLocation,
    ConstraintNode,
    ConstraintType,
    IntegrationNode
)

class RequirementParser:
    """
    Parses a token stream into a RequirementAST.
    Uses heuristic and rule-based parsing.
    """

    def __init__(self):
        pass

    def parse(self, tokens: list[Token], raw_text: str = "") -> RequirementAST:
        ast = RequirementAST()
        ast.metadata.source_hash = hashlib.sha256(raw_text.encode()).hexdigest()
        ast.metadata.token_count = len(tokens)
        
        if not tokens:
            return ast

        entities = {}
        features = {}
        roles = {}
        plans = {}
        integrations = {}
        
        i = 0
        n = len(tokens)
        while i < n:
            t = tokens[i]
            
            # Simple inference based on current token
            if t.type == TokenType.ENTITY:
                if t.value not in entities:
                    entities[t.value] = EntityNode(
                        name=t.value,
                        source=SourceLocation(line=t.line, column=t.position, length=len(t.raw), raw_text=t.raw)
                    )
            elif t.type == TokenType.FEATURE:
                if t.value not in features:
                    features[t.value] = FeatureNode(
                        name=t.value,
                        feature_type=FeatureType.PAGE if t.value in {"dashboard", "panel", "board"} else FeatureType.SERVICE,
                        source=SourceLocation(line=t.line, column=t.position, length=len(t.raw), raw_text=t.raw)
                    )
            elif t.type == TokenType.ROLE:
                if t.value not in roles:
                    roles[t.value] = RoleNode(
                        name=t.value,
                        source=SourceLocation(line=t.line, column=t.position, length=len(t.raw), raw_text=t.raw)
                    )
            elif t.type == TokenType.PLAN:
                if t.value not in plans:
                    tier = 0
                    if t.value in {"basic", "starter"}: tier = 1
                    elif t.value in {"premium", "pro", "business"}: tier = 2
                    elif t.value == "enterprise": tier = 3
                    
                    plans[t.value] = PlanNode(
                        name=t.value,
                        tier=tier,
                        source=SourceLocation(line=t.line, column=t.position, length=len(t.raw), raw_text=t.raw)
                    )
            elif t.type == TokenType.INTEGRATION:
                if t.value not in integrations:
                    integrations[t.value] = IntegrationNode(
                        name=t.value,
                        integration_type=t.value,
                        source=SourceLocation(line=t.line, column=t.position, length=len(t.raw), raw_text=t.raw)
                    )
            elif t.type == TokenType.ACTION:
                if t.value == "login":
                    if "user" not in entities:
                        entities["user"] = EntityNode(name="user", is_auth_entity=True)
                    else:
                        entities["user"].is_auth_entity = True
                
            i += 1

        ast.entities = list(entities.values())
        ast.features = list(features.values())
        ast.roles = list(roles.values())
        ast.plans = list(plans.values())
        ast.integrations = list(integrations.values())
        
        # Add basic constraints if "role-based" or "premium" are found
        for t in tokens:
            if t.type == TokenType.CONSTRAINT:
                if t.value == "role-based":
                    ast.constraints.append(ConstraintNode(
                        constraint_type=ConstraintType.ACCESS_CONTROL,
                        target="global",
                        description="Role-based access control enabled"
                    ))
                elif t.value == "premium":
                    ast.constraints.append(ConstraintNode(
                        constraint_type=ConstraintType.PAYMENT_GATE,
                        target="features",
                        description="Premium feature gating enabled"
                    ))
        
        ast.metadata.node_count = ast.total_nodes
        return ast
