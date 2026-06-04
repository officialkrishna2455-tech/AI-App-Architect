import os
import json
import sys
from pathlib import Path

# Add backend to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema
)

def export_schemas():
    output_dir = Path(__file__).parent.parent / "schemas_export"
    output_dir.mkdir(exist_ok=True)
    
    schemas = {
        "RequirementAST.json": RequirementAST,
        "UISchema.json": UISchema,
        "APISchema.json": APISchema,
        "DBSchema.json": DBSchema,
        "AuthSchema.json": AuthSchema,
        "BusinessLogicSchema.json": BusinessLogicSchema,
    }
    
    for filename, model in schemas.items():
        filepath = output_dir / filename
        schema_json = model.model_json_schema()
        with open(filepath, "w") as f:
            json.dump(schema_json, f, indent=2)
            
    print(f"Exported {len(schemas)} JSON Schemas to {output_dir}")

if __name__ == "__main__":
    export_schemas()
