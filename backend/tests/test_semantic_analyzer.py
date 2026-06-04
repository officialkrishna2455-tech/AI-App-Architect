import pytest
from app.schemas.ast_models import RequirementAST, EntityNode, FeatureNode, RoleNode
from app.compiler.semantic_analyzer import SemanticAnalyzer

def test_semantic_analyzer_adds_default_fields():
    ast = RequirementAST()
    ast.entities.append(EntityNode(name="product"))
    
    analyzer = SemanticAnalyzer()
    enriched_ast = analyzer.analyze(ast)
    
    fields = [f.name for f in enriched_ast.entities[0].fields]
    assert "id" in fields
    assert "created_at" in fields
    assert "updated_at" in fields

def test_semantic_analyzer_infers_auth_fields():
    ast = RequirementAST()
    ast.entities.append(EntityNode(name="user", is_auth_entity=True))
    
    analyzer = SemanticAnalyzer()
    enriched_ast = analyzer.analyze(ast)
    
    fields = [f.name for f in enriched_ast.entities[0].fields]
    assert "email" in fields
    assert "password_hash" in fields
    assert "is_active" in fields

def test_semantic_analyzer_infers_relations():
    ast = RequirementAST()
    ast.entities.append(EntityNode(name="user"))
    ast.entities.append(EntityNode(name="contact"))
    
    analyzer = SemanticAnalyzer()
    enriched_ast = analyzer.analyze(ast)
    
    user_entity = enriched_ast.get_entity("user")
    contact_entity = enriched_ast.get_entity("contact")
    
    assert any(r.target_entity == "contact" for r in user_entity.relations)
    assert any(f.name == "user_id" for f in contact_entity.fields)

def test_semantic_analyzer_generates_permissions():
    ast = RequirementAST()
    ast.entities.append(EntityNode(name="product"))
    ast.roles.append(RoleNode(name="admin"))
    
    analyzer = SemanticAnalyzer()
    enriched_ast = analyzer.analyze(ast)
    
    admin_role = enriched_ast.get_role("admin")
    assert len(admin_role.permissions) == 1
    assert admin_role.permissions[0].resource == "product"
