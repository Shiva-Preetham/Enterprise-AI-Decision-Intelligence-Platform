import api from './api';
import type {
  SuccessResponse, PaginatedResponse, Customer, CustomerProfile,
  TimelineEvent, DashboardMetrics, PredictionResult, SHAPExplanation,
  Recommendation, Workflow, AuditEvent, ChatRequest, AgentResponse,
  ModelVersion, Experiment, DriftReport, Alert, DataQualityReport,
  TaskTrigger, TaskStatus, HealthStatus,
} from '../types';

// --- Customers ---
export const customerService = {
  list: (skip = 0, limit = 20) =>
    api.get<SuccessResponse<PaginatedResponse<Customer>>>(`/api/v1/customers?skip=${skip}&limit=${limit}`).then(r => r.data.data),
  getProfile: (id: string) =>
    api.get<SuccessResponse<CustomerProfile>>(`/api/v1/customers/${id}/profile`).then(r => r.data.data),
  getTimeline: (id: string) =>
    api.get<SuccessResponse<{ events: TimelineEvent[] }>>(`/api/v1/customers/${id}/timeline`).then(r => r.data.data),
};

// --- Analytics ---
export const analyticsService = {
  getDashboard: () =>
    api.get<SuccessResponse<DashboardMetrics>>('/api/v1/analytics/dashboard').then(r => r.data.data),
  getRFM: () =>
    api.get<SuccessResponse<Record<string, unknown>>>('/api/v1/analytics/rfm').then(r => r.data.data),
};

// --- Predictions ---
export const predictionService = {
  predict: (customerId: string) =>
    api.post<SuccessResponse<PredictionResult>>('/api/v1/predict', { customer_id: customerId }).then(r => r.data.data),
  explain: (customerId: string) =>
    api.get<SuccessResponse<SHAPExplanation>>(`/api/v1/predict/${customerId}/explanation`).then(r => r.data.data),
};

// --- Decisions ---
export const decisionService = {
  recommend: (customerId: string) =>
    api.post<Recommendation>(`/api/v1/decisions/recommend?customer_id=${customerId}`).then(r => r.data),
  getWorkflow: (id: string) =>
    api.get<Workflow>(`/api/v1/decisions/workflow/${id}`).then(r => r.data),
  approveWorkflow: (id: string, approverId: string) =>
    api.post<Workflow>(`/api/v1/decisions/workflow/${id}/approve`, { approver_id: approverId }).then(r => r.data),
  rejectWorkflow: (id: string, approverId: string, reason: string) =>
    api.post<Workflow>(`/api/v1/decisions/workflow/${id}/reject`, { approver_id: approverId, reason }).then(r => r.data),
  executeWorkflow: (id: string) =>
    api.post(`/api/v1/decisions/workflow/${id}/execute`).then(r => r.data),
  getAudit: (workflowId: string) =>
    api.get<AuditEvent[]>(`/api/v1/decisions/audit/${workflowId}`).then(r => r.data),
};

// --- Agent ---
export const agentService = {
  chat: (request: ChatRequest) =>
    api.post<AgentResponse>('/api/v1/agent/chat', request).then(r => r.data),
};

// --- MLOps ---
export const mlopsService = {
  listModels: () =>
    api.get<ModelVersion[]>('/api/v1/mlops/models').then(r => r.data),
  getModel: (version: number) =>
    api.get<ModelVersion>(`/api/v1/mlops/models/${version}`).then(r => r.data),
  rollbackModel: (version: number) =>
    api.post<ModelVersion>(`/api/v1/mlops/models/${version}/rollback`).then(r => r.data),
  listExperiments: () =>
    api.get<Experiment[]>('/api/v1/mlops/experiments').then(r => r.data),
  getDrift: () =>
    api.get<DriftReport[]>('/api/v1/mlops/drift').then(r => r.data),
  getDataQuality: () =>
    api.get<DataQualityReport>('/api/v1/mlops/data-quality').then(r => r.data),
  listAlerts: () =>
    api.get<Alert[]>('/api/v1/mlops/alerts').then(r => r.data),
};

// --- Tasks ---
export const taskService = {
  triggerTrain: () =>
    api.post<SuccessResponse<TaskTrigger>>('/api/v1/tasks/train').then(r => r.data.data),
  triggerFeatureStore: () =>
    api.post<SuccessResponse<TaskTrigger>>('/api/v1/tasks/feature-store').then(r => r.data.data),
  triggerBatchPredict: () =>
    api.post<SuccessResponse<TaskTrigger>>('/api/v1/tasks/batch-predict').then(r => r.data.data),
  getStatus: (taskId: string) =>
    api.get<SuccessResponse<TaskStatus>>(`/api/v1/tasks/${taskId}`).then(r => r.data.data),
};

// --- Health ---
export const healthService = {
  getHealth: () =>
    api.get<SuccessResponse<HealthStatus>>('/api/v1/health').then(r => r.data.data),
  getMetrics: () =>
    api.get('/metrics').then(r => r.data),
};
