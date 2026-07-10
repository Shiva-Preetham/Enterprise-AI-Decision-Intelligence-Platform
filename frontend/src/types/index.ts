/* ===================================================================
   TypeScript interfaces mirroring backend Pydantic schemas.
   One file per domain, re-exported from index.ts.
   =================================================================== */

// --- Common ---
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface SuccessResponse<T = unknown> {
  message: string;
  data: T;
}

// --- Auth ---
export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  role: UserRole;
}

export type UserRole = 'admin' | 'manager' | 'analyst' | 'viewer';

export interface User {
  id: string;
  username: string;
  role: UserRole;
}

// --- Customer ---
export interface Customer {
  customer_unique_id: string;
  customer_city: string | null;
  customer_state: string | null;
}

export interface CustomerFeatures {
  customer_unique_id: string;
  total_lifetime_value: number;
  average_order_value: number;
  purchase_count: number;
  days_since_last_purchase: number;
  review_score_mean: number;
  freight_value_sum: number;
}

export interface CustomerProfile {
  customer: Customer;
  features: CustomerFeatures | null;
  prediction: PredictionResult | null;
}

export interface TimelineEvent {
  type: string;
  date: string;
  details: Record<string, unknown>;
}

// --- Prediction ---
export interface PredictionResult {
  customer_id: string;
  probability: number;
  label: string;
  risk_level: string;
}

export interface SHAPExplanation {
  customer_id: string;
  base_value: number;
  shap_values: Record<string, number>;
  feature_values: Record<string, number>;
  prediction: number;
}

// --- Analytics ---
export interface DashboardMetrics {
  total_customers: number;
  high_risk_customers: number;
  average_clv: number;
  average_review_score: number;
  churn_rate: number;
  model_version: string | null;
}

// --- Decision Engine ---
export interface Recommendation {
  recommendation_id: string;
  customer_unique_id: string;
  recommendation_type: string;
  priority: string;
  confidence: number;
  business_reason: string;
  expected_impact: string;
  estimated_cost: number | null;
  required_approval: boolean;
  generated_by: string;
  created_at: string;
}

export interface Workflow {
  workflow_id: string;
  recommendation_id: string;
  status: WorkflowStatus;
  created_at: string;
  updated_at: string;
}

export type WorkflowStatus =
  | 'Created'
  | 'PendingApproval'
  | 'Approved'
  | 'Executing'
  | 'Completed'
  | 'Failed'
  | 'Cancelled';

export interface AuditEvent {
  audit_id: string;
  workflow_id: string | null;
  customer_unique_id: string;
  event_type: string;
  details: string;
  created_at: string;
}

// --- Agent ---
export interface ChatRequest {
  question: string;
  customer_id?: string;
  conversation_id?: string;
}

export interface AgentResponse {
  answer: string;
  reasoning: string;
  tools_used: string[];
  follow_up_questions: string[];
  confidence: number;
}

// --- MLOps ---
export interface ModelVersion {
  model_id: string;
  version: number;
  training_timestamp: string;
  dataset_version: string;
  feature_version: string;
  pipeline_version: string;
  hyperparameters: string;
  metrics: string;
  shap_summary: string;
  deployment_status: string;
  filename: string;
}

export interface Experiment {
  experiment_id: string;
  run_id: string;
  timestamp: string;
  duration_seconds: number;
  params: string;
  metrics: string;
  dataset_ref: string;
  feature_count: number;
  algorithm: string;
  cv_scores: string;
}

export interface DriftReport {
  report_id: string;
  timestamp: string;
  reference_window_start: string;
  reference_window_end: string;
  current_window_start: string;
  current_window_end: string;
  feature_stats: string;
  is_alert: boolean;
}

export interface Alert {
  alert_id: string;
  timestamp: string;
  alert_type: string;
  severity: string;
  details: string;
  status: string;
}

export interface DataQualityReport {
  timestamp: string;
  total_rows: number;
  missing_value_rates: Record<string, number>;
  duplicate_rows: number;
  out_of_range_features: string[];
  schema_mismatches: string[];
  overall_status: string;
}

// --- Tasks ---
export interface TaskTrigger {
  task_id: string;
  task_name: string;
  status: string;
  message: string;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: Record<string, unknown> | null;
  result: Record<string, unknown> | null;
  error: string | null;
  duration_seconds: number | null;
}

export interface HealthStatus {
  api_status: string;
  database_status: string;
  database_error: string | null;
  ml_model_loaded: boolean;
  application_version: string;
  environment: string;
  pipeline_version: string;
  feature_version: string;
  uptime_seconds: number;
  timestamp: string;
}
