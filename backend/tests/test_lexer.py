import pytest
from app.compiler.requirement_lexer import RequirementLexer
from app.schemas.ast_models import TokenType

def test_lexer_tokenizes_entities_and_actions():
    lexer = RequirementLexer()
    # Mock spacy if not available
    text = "Build a CRM with user login and contact management"
    tokens = lexer.tokenize(text)
    
    token_values = [t.value for t in tokens]
    assert "user" in token_values
    assert "login" in token_values
    assert "contact" in token_values
    
    # Check types
    for t in tokens:
        if t.value == "user":
            assert t.type == TokenType.ENTITY
        elif t.value == "login":
            assert t.type == TokenType.ACTION
        elif t.value == "contact":
            assert t.type == TokenType.ENTITY

def test_lexer_handles_plural_entities():
    lexer = RequirementLexer()
    text = "users can create orders"
    tokens = lexer.tokenize(text)
    
    token_values = [t.value for t in tokens]
    assert "user" in token_values
    assert "order" in token_values
    
    user_token = next(t for t in tokens if t.value == "user")
    assert user_token.type == TokenType.ENTITY

def test_lexer_handles_roles_and_constraints():
    lexer = RequirementLexer()
    text = "admin role-based premium features"
    tokens = lexer.tokenize(text)
    
    assert any(t.type == TokenType.ROLE and t.value == "admin" for t in tokens)
    assert any(t.type == TokenType.CONSTRAINT and t.value == "role-based" for t in tokens)
    assert any(t.type == TokenType.CONSTRAINT and t.value == "premium" for t in tokens)
