import time
import asyncio
from typing import Callable, Optional

from app.schemas.requests import CompileOptions
from app.schemas.responses import CompileResponse, StageLatency, CompileMetrics, SchemaOutput, KnowledgeGraphOutput

from app.compiler.requirement_lexer import RequirementLexer
from app.compiler.requirement_parser import RequirementParser
from app.compiler.semantic_analyzer import SemanticAnalyzer
from app.compiler.architecture_planner import ArchitecturePlanner
from app.compiler.schema_generator import SchemaGenerator
from app.compiler.consistency_engine import ConsistencyEngine
from app.compiler.validation_engine import ValidationEngine
from app.compiler.repair_engine import RepairEngine
from app.compiler.runtime_simulator import RuntimeSimulator

class CompilationPipeline:
    """
    Orchestrates the 9-stage compilation pipeline.
    """

    def __init__(self):
        self.lexer = RequirementLexer()
        self.parser = RequirementParser()
        self.semantic_analyzer = SemanticAnalyzer()
        self.arch_planner = ArchitecturePlanner()
        self.schema_generator = SchemaGenerator()
        self.consistency_engine = ConsistencyEngine()
        self.validation_engine = ValidationEngine()
        self.repair_engine = RepairEngine()
        self.simulator = RuntimeSimulator()

    def compile_sync(self, requirements: str, options: CompileOptions, run_id: str = "sync_run") -> CompileResponse:
        start_total = time.time()
        metrics = CompileMetrics()
        
        def track_time(stage_name: str, func, *args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            latency = int((time.time() - start) * 1000)
            metrics.stage_latencies.append(StageLatency(stage=stage_name, latency_ms=latency))
            return result

        # 1. Lexer
        tokens = track_time("lexer", self.lexer.tokenize, requirements)
        metrics.token_count = len(tokens)
        
        # 2. Parser
        ast = track_time("parser", self.parser.parse, tokens, requirements)
        metrics.node_count = ast.total_nodes
        
        # 3. Semantic Analyzer
        enriched_ast = track_time("semantic_analyzer", self.semantic_analyzer.analyze, ast)
        
        # 4. Architecture Planner
        arch_plan = track_time("architecture_planner", self.arch_planner.plan, enriched_ast)
        
        # 5. Schema Generator
        spec = track_time("schema_generator", self.schema_generator.generate_all, enriched_ast, arch_plan)
        
        # 6. Consistency Engine
        graph, graph_issues = track_time(
            "consistency_engine", 
            self.consistency_engine.check, 
            spec.ast, spec.ui_schema, spec.api_schema, spec.db_schema, spec.auth_schema, spec.business_logic
        )
        
        # 7. Validation Engine
        validation_report = track_time(
            "validation_engine", 
            self.validation_engine.validate,
            spec.ast, spec.ui_schema, spec.api_schema, spec.db_schema, spec.auth_schema, spec.business_logic, graph_issues
        )
        metrics.validation_pass_rate = 1.0 if validation_report.passed else 0.0
        
        # 8. Repair Engine
        repaired_spec, repair_report = track_time(
            "repair_engine",
            self.repair_engine.repair,
            spec, validation_report, options.max_repair_iterations
        )
        metrics.repair_count = repair_report.total_repairs
        
        # 9. Runtime Simulator & Self-Healing Loop
        simulation_report = None
        if options.include_simulation:
            categories = ["crud", "auth", "authorization", "navigation", "premium", "flow"]
            simulation_report = track_time(
                "runtime_simulator",
                self.simulator.simulate,
                repaired_spec.ast, repaired_spec, categories
            )
            
            # Self-Healing Loop
            repair_cycles = 0
            all_repair_actions = []
            
            while (
                simulation_report.pass_rate < 1.0 and 
                repair_cycles < options.max_simulation_repair_iterations
            ):
                repair_cycles += 1
                
                # a. Convert failures to ValidationIssues
                sim_issues = self.simulator.failures_to_issues(simulation_report)
                if not sim_issues:
                    break
                    
                # Create a synthetic validation report for the repair engine
                from app.schemas.ast_models import ValidationReport
                sim_validation_report = ValidationReport(issues=sim_issues)
                
                # b. Feed into Repair Engine
                repaired_spec, sim_repair_report = self.repair_engine.repair(
                    repaired_spec, sim_validation_report, max_iterations=1
                )
                
                # Record repair actions taken
                if sim_repair_report.repairs:
                    all_repair_actions.extend([
                        {"rule_id": r.issue_rule_id, "action": r.action_type, "target": r.target_path}
                        for r in sim_repair_report.repairs
                    ])
                    # Accumulate repair count in metrics
                    metrics.repair_count += sim_repair_report.total_repairs
                
                # c. Revalidate
                _ = self.validation_engine.validate(
                    repaired_spec.ast, repaired_spec.ui_schema, repaired_spec.api_schema,
                    repaired_spec.db_schema, repaired_spec.auth_schema, repaired_spec.business_logic
                )
                
                # d. Re-simulate
                simulation_report = track_time(
                    f"runtime_simulator_cycle_{repair_cycles}",
                    self.simulator.simulate,
                    repaired_spec.ast, repaired_spec, categories
                )
            
            if simulation_report:
                simulation_report.repair_cycles = repair_cycles
                simulation_report.auto_repaired = repair_cycles > 0
                simulation_report.repairs_triggered = all_repair_actions
                metrics.simulation_pass_rate = simulation_report.pass_rate
            
        metrics.total_latency_ms = int((time.time() - start_total) * 1000)
        
        # Format response
        schema_out = SchemaOutput(
            ui_schema=repaired_spec.ui_schema,
            api_schema=repaired_spec.api_schema,
            db_schema=repaired_spec.db_schema,
            auth_schema=repaired_spec.auth_schema,
            business_logic_schema=repaired_spec.business_logic
        )
        
        kg_out = KnowledgeGraphOutput()
        if options.include_knowledge_graph and graph:
            kg_dict = graph.to_dict()
            kg_out = KnowledgeGraphOutput(
                nodes=kg_dict["nodes"],
                edges=kg_dict["edges"],
                node_count=kg_dict["node_count"],
                edge_count=kg_dict["edge_count"]
            )
            
        return CompileResponse(
            run_id=run_id,
            status="completed",
            ast=repaired_spec.ast,
            schemas=schema_out,
            validation_report=validation_report,
            repair_report=repair_report,
            simulation_report=simulation_report,
            knowledge_graph=kg_out,
            metrics=metrics
        )

    async def compile(self, requirements: str, options: CompileOptions, run_id: str, status_callback: Optional[Callable] = None) -> CompileResponse:
        # Real async implementation would use thread pools for CPU bound tasks
        # For this prototype, we'll run the sync version in an executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.compile_sync, requirements, options, run_id)
