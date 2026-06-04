from typing import Optional

from app.schemas.ast_models import (
    RequirementAST,
    FieldNode,
    FieldType,
    RelationNode,
    RelationType,
    PermissionNode,
    ActionVerb,
    FeatureType,
    FeatureNode
)


class SemanticAnalyzer:
    """
    Enriches the AST with inferred semantics: fields, relations, permissions.
    """

    def analyze(self, ast: RequirementAST) -> RequirementAST:
        # We modify the AST in place for simplicity (or we could copy it)
        
        # 1. Enrich Entities with default fields
        for entity in ast.entities:
            existing_fields = {f.name for f in entity.fields}
            
            # Common fields
            if "id" not in existing_fields:
                entity.fields.append(FieldNode(name="id", field_type=FieldType.UUID, required=True, unique=True, indexed=True))
            if entity.timestamps:
                if "created_at" not in existing_fields:
                    entity.fields.append(FieldNode(name="created_at", field_type=FieldType.DATETIME, required=True))
                if "updated_at" not in existing_fields:
                    entity.fields.append(FieldNode(name="updated_at", field_type=FieldType.DATETIME, required=True))
            
            # Specific entity type inference
            if entity.is_auth_entity:
                if "email" not in existing_fields:
                    entity.fields.append(FieldNode(name="email", field_type=FieldType.EMAIL, required=True, unique=True, indexed=True))
                if "password_hash" not in existing_fields:
                    entity.fields.append(FieldNode(name="password_hash", field_type=FieldType.STRING, required=True))
                if "is_active" not in existing_fields:
                    entity.fields.append(FieldNode(name="is_active", field_type=FieldType.BOOLEAN, default=True))
            
            if entity.name == "contact":
                if "first_name" not in existing_fields:
                    entity.fields.append(FieldNode(name="first_name", field_type=FieldType.STRING))
                if "last_name" not in existing_fields:
                    entity.fields.append(FieldNode(name="last_name", field_type=FieldType.STRING))
                if "email" not in existing_fields:
                    entity.fields.append(FieldNode(name="email", field_type=FieldType.EMAIL))
                
        # 2. Enrich Relations
        # If user and contact exist, assume User has many Contacts
        entity_names = ast.entity_names()
        if "user" in entity_names and "contact" in entity_names:
            user_entity = ast.get_entity("user")
            contact_entity = ast.get_entity("contact")
            
            if not any(r.target_entity == "contact" for r in user_entity.relations):
                user_entity.relations.append(RelationNode(
                    target_entity="contact",
                    relation_type=RelationType.ONE_TO_MANY,
                    back_reference="user"
                ))
            if not any(f.name == "user_id" for f in contact_entity.fields):
                contact_entity.fields.append(FieldNode(name="user_id", field_type=FieldType.UUID))

        # 3. Permissions Matrix
        if ast.roles:
            admin_role = ast.get_role("admin") or ast.get_role("owner") or ast.get_role("superadmin")
            if admin_role:
                for entity in ast.entities:
                    if not any(p.resource == entity.name for p in admin_role.permissions):
                        admin_role.permissions.append(PermissionNode(
                            resource=entity.name,
                            actions=[ActionVerb.CREATE, ActionVerb.READ, ActionVerb.UPDATE, ActionVerb.DELETE]
                        ))
            
            user_role = ast.get_role("user")
            if user_role:
                for entity in ast.entities:
                    if not any(p.resource == entity.name for p in user_role.permissions):
                        # Heuristic: Users can read and update their own things
                        user_role.permissions.append(PermissionNode(
                            resource=entity.name,
                            actions=[ActionVerb.CREATE, ActionVerb.READ, ActionVerb.UPDATE],
                            conditions={"own_only": True}
                        ))
                        
        # 4. Feature dependencies
        for feature in ast.features:
            if feature.name == "dashboard":
                feature.entities = [e.name for e in ast.entities] # Dashboard depends on all entities
                feature.feature_type = FeatureType.PAGE
                
        # 5. Metadata enrichments
        ast.metadata.enrichments.append("Added default fields (id, timestamps) to entities.")
        ast.metadata.enrichments.append("Generated default admin/user permissions.")
        
        ast.metadata.node_count = ast.total_nodes
        
        return ast
