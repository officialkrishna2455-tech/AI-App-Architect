from app.knowledge_graph.graph import KnowledgeGraph
from app.schemas.ast_models import ValidationIssue, Severity

class GraphValidator:
    """
    Runs graph-based validation rules.
    """

    def validate(self, graph: KnowledgeGraph) -> list[ValidationIssue]:
        issues = []
        
        # Check dangling references
        ref_errors = graph.validate_references()
        for err in ref_errors:
            issues.append(ValidationIssue(
                rule_id="G001",
                severity=Severity.ERROR,
                layer="cross_layer",
                message=err,
                affected_schema="graph"
            ))
            
        # Check for pages that call missing endpoints
        from app.knowledge_graph.entities import NodeType, EdgeType
        for node_id, node in graph.nodes.items():
            if node.node_type == NodeType.PAGE:
                called_eps = graph.get_neighbors(node_id, EdgeType.CALLS)
                for ep_id in called_eps:
                    if ep_id not in graph.nodes:
                        issues.append(ValidationIssue(
                            rule_id="V005",
                            severity=Severity.WARNING,
                            layer="cross_layer",
                            message=f"Page {node.label} references missing API endpoint {ep_id}",
                            affected_schema="ui",
                            affected_path=f"pages.[route='{node.properties.get('route')}'].data_sources"
                        ))

            elif node.node_type == NodeType.ENDPOINT:
                # Check endpoints referencing missing entities
                ref_entities = graph.get_neighbors(node_id, EdgeType.REFERENCES)
                for ent_id in ref_entities:
                    if ent_id not in graph.nodes:
                        issues.append(ValidationIssue(
                            rule_id="V004",
                            severity=Severity.ERROR,
                            layer="cross_layer",
                            message=f"API Endpoint {node.label} references missing entity {ent_id}",
                            affected_schema="api",
                            affected_path=f"endpoints.[path='{node.label}']"
                        ))
                        
        return issues
