import pytest
from app.schemas.ast_models import Token, TokenType, RequirementAST
from app.compiler.requirement_parser import RequirementParser

def test_parser_extracts_entities_and_features():
    parser = RequirementParser()
    tokens = [
        Token(type=TokenType.UNKNOWN, value="build", raw="Build", position=0, line=1, confidence=0.5),
        Token(type=TokenType.ENTITY, value="user", raw="user", position=6, line=1, confidence=1.0),
        Token(type=TokenType.ACTION, value="login", raw="login", position=11, line=1, confidence=1.0),
        Token(type=TokenType.FEATURE, value="dashboard", raw="dashboard", position=17, line=1, confidence=1.0),
    ]
    
    ast = parser.parse(tokens, "Build user login dashboard")
    
    assert len(ast.entities) == 1
    assert ast.entities[0].name == "user"
    assert ast.entities[0].is_auth_entity == True
    
    assert len(ast.features) == 1
    assert ast.features[0].name == "dashboard"

def test_parser_extracts_roles_and_plans():
    parser = RequirementParser()
    tokens = [
        Token(type=TokenType.ROLE, value="admin", raw="admin", position=0, line=1, confidence=1.0),
        Token(type=TokenType.PLAN, value="enterprise", raw="enterprise", position=6, line=1, confidence=1.0),
        Token(type=TokenType.CONSTRAINT, value="premium", raw="premium", position=17, line=1, confidence=1.0),
    ]
    
    ast = parser.parse(tokens, "admin enterprise premium")
    
    assert len(ast.roles) == 1
    assert ast.roles[0].name == "admin"
    
    assert len(ast.plans) == 1
    assert ast.plans[0].name == "enterprise"
    assert ast.plans[0].tier == 3
    
    assert len(ast.constraints) == 1
    assert ast.constraints[0].description == "Premium feature gating enabled"
