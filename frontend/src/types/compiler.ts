// Mirrors backend Pydantic models

export type TokenType = "entity" | "action" | "feature" | "role" | "constraint" | "relation" | "modifier" | "plan" | "integration" | "field_type" | "punctuation" | "connector" | "quantifier" | "unknown";

export interface Token {
  type: TokenType;
  value: string;
  raw: string;
  position: number;
  line: number;
  confidence: number;
}

export interface FieldNode {
  node_type: "field";
  name: string;
  field_type: string;
  required: boolean;
  unique: boolean;
  indexed: boolean;
  default?: any;
  enum_values?: string[];
  description: string;
}

export interface RelationNode {
  node_type: "relation";
  target_entity: string;
  relation_type: string;
  foreign_key?: string;
  cascade_delete: boolean;
  back_reference?: string;
}

export interface PermissionNode {
  node_type: "permission";
  resource: string;
  actions: string[];
  conditions?: Record<string, any>;
}

export interface ActionNode {
  node_type: "action";
  verb: string;
  target_entity: string;
  required_roles: string[];
  required_plan?: string;
  custom_logic?: string;
}

export interface ConstraintNode {
  node_type: "constraint";
  constraint_type: string;
  target: string;
  parameters: Record<string, any>;
  description: string;
}

export interface EntityNode {
  node_type: "entity";
  name: string;
  fields: FieldNode[];
  relations: RelationNode[];
  is_auth_entity: boolean;
  soft_delete: boolean;
  timestamps: boolean;
  description: string;
}

export interface FeatureNode {
  node_type: "feature";
  name: string;
  feature_type: string;
  entities: string[];
  actions: ActionNode[];
  constraints: ConstraintNode[];
  auth_required: boolean;
  required_roles: string[];
  required_plan?: string;
  sub_features: string[];
  description: string;
}

export interface RoleNode {
  node_type: "role";
  name: string;
  is_default: boolean;
  parent_role?: string;
  permissions: PermissionNode[];
  description: string;
}

export interface RequirementAST {
  entities: EntityNode[];
  features: FeatureNode[];
  roles: RoleNode[];
  plans: any[];
  integrations: any[];
  constraints: ConstraintNode[];
  metadata: any;
}

export interface UISchema {
  pages: any[];
  components: any[];
  navigation: any[];
  theme: any;
}

export interface APISchema {
  base_path: string;
  endpoints: any[];
  middleware: any[];
  error_codes: any;
}

export interface DBSchema {
  tables: any[];
  indexes: any[];
  relations: any[];
  migrations: any[];
}

export interface AuthSchema {
  provider: string;
  roles: any[];
  permissions: any[];
  policies: any[];
  token_config: any;
}

export interface BusinessLogicSchema {
  workflows: any[];
  rules: any[];
  events: any[];
  integrations: any[];
}

export interface SchemaOutput {
  ui_schema: UISchema;
  api_schema: APISchema;
  db_schema: DBSchema;
  auth_schema: AuthSchema;
  business_logic_schema: BusinessLogicSchema;
}

export interface ValidationIssue {
  rule_id: string;
  severity: "error" | "warning" | "info";
  layer: string;
  message: string;
  affected_schema: string;
  affected_path: string;
  suggestion: string;
}

export interface ValidationReport {
  total_issues: number;
  errors: number;
  warnings: number;
  infos: number;
  issues: ValidationIssue[];
  passed: boolean;
  validation_time_ms: number;
}

export interface RepairAction {
  issue_rule_id: string;
  action_type: string;
  target_schema: string;
  target_path: string;
  description: string;
  before_value?: any;
  after_value?: any;
}

export interface RepairReport {
  total_repairs: number;
  repairs: RepairAction[];
  unresolvable: ValidationIssue[];
  repair_time_ms: number;
}

export interface SimulationScenario {
  scenario_id: string;
  category: string;
  description: string;
  steps: string[];
  expected_result: string;
  actual_result: string;
  passed: boolean;
  error_message: string;
}

export interface SimulationReport {
  total_scenarios: number;
  passed_count: number;
  failed_count: number;
  scenarios: SimulationScenario[];
  simulation_time_ms: number;
}

export interface StageLatency {
  stage: string;
  latency_ms: number;
  status: string;
}

export interface CompileMetrics {
  total_latency_ms: number;
  stage_latencies: StageLatency[];
  token_count: number;
  node_count: number;
  validation_pass_rate: number;
  repair_count: number;
  simulation_pass_rate: number;
}

export interface CompileResponse {
  run_id: string;
  status: string;
  ast: RequirementAST;
  schemas: SchemaOutput;
  validation_report: ValidationReport;
  repair_report: RepairReport;
  simulation_report: SimulationReport;
  knowledge_graph: any;
  metrics: CompileMetrics;
}

export interface RunSummary {
  run_id: string;
  status: string;
  requirements_preview: string;
  total_latency_ms: number;
  validation_pass_rate: number;
  simulation_pass_rate: number;
  entity_count: number;
  feature_count: number;
  created_at: string;
  updated_at: string;
}

export interface RunListResponse {
  runs: RunSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface MetricsResponse {
  total_runs: number;
  success_rate: number;
  average_latency_ms: number;
  average_repair_rate: number;
  average_validation_pass_rate: number;
  average_simulation_pass_rate: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
}

export interface EvalPromptResult {
  prompt_id: number;
  prompt_type: string;
  prompt_text: string;
  success: boolean;
  validation_pass_rate: number;
  simulation_pass_rate: number;
  repair_count: number;
  latency_ms: number;
  error_message: string;
}

export interface EvalRunResponse {
  total_prompts: number;
  success_count: number;
  success_rate: number;
  results: EvalPromptResult[];
  aggregate_metrics: MetricsResponse;
}
