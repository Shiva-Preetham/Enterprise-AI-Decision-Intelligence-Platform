import { useQuery, useMutation } from '@tanstack/react-query';
import {
  customerService, analyticsService, predictionService,
  decisionService, agentService, mlopsService, healthService,
} from '../services';
import type { ChatRequest } from '../types';

// --- Customers ---
export const useCustomers = (skip = 0, limit = 20) =>
  useQuery({ queryKey: ['customers', skip, limit], queryFn: () => customerService.list(skip, limit) });

export const useCustomerProfile = (id: string) =>
  useQuery({ queryKey: ['customer', id], queryFn: () => customerService.getProfile(id), enabled: !!id });

export const useCustomerTimeline = (id: string) =>
  useQuery({ queryKey: ['timeline', id], queryFn: () => customerService.getTimeline(id), enabled: !!id });

// --- Analytics ---
export const useDashboard = () =>
  useQuery({ queryKey: ['dashboard'], queryFn: analyticsService.getDashboard, refetchInterval: 60000 });

// --- Predictions ---
export const usePrediction = (customerId: string) =>
  useMutation({ mutationFn: () => predictionService.predict(customerId) });

export const useSHAPExplanation = (customerId: string) =>
  useQuery({ queryKey: ['shap', customerId], queryFn: () => predictionService.explain(customerId), enabled: !!customerId });

// --- Decisions ---
export const useRecommend = () =>
  useMutation({ mutationFn: (customerId: string) => decisionService.recommend(customerId) });

export const useWorkflow = (id: string) =>
  useQuery({ queryKey: ['workflow', id], queryFn: () => decisionService.getWorkflow(id), enabled: !!id });

export const useApproveWorkflow = () =>
  useMutation({ mutationFn: ({ id, approverId }: { id: string; approverId: string }) => decisionService.approveWorkflow(id, approverId) });

export const useRejectWorkflow = () =>
  useMutation({ mutationFn: ({ id, approverId, reason }: { id: string; approverId: string; reason: string }) => decisionService.rejectWorkflow(id, approverId, reason) });

export const useAuditTrail = (workflowId: string) =>
  useQuery({ queryKey: ['audit', workflowId], queryFn: () => decisionService.getAudit(workflowId), enabled: !!workflowId });

// --- Agent ---
export const useAgentChat = () =>
  useMutation({ mutationFn: (request: ChatRequest) => agentService.chat(request) });

// --- MLOps ---
export const useModels = () =>
  useQuery({ queryKey: ['models'], queryFn: mlopsService.listModels });

export const useExperiments = () =>
  useQuery({ queryKey: ['experiments'], queryFn: mlopsService.listExperiments });

export const useDrift = () =>
  useQuery({ queryKey: ['drift'], queryFn: mlopsService.getDrift });

export const useDataQuality = () =>
  useQuery({ queryKey: ['data-quality'], queryFn: mlopsService.getDataQuality });

export const useAlerts = () =>
  useQuery({ queryKey: ['alerts'], queryFn: mlopsService.listAlerts });

export const useRollbackModel = () =>
  useMutation({ mutationFn: (version: number) => mlopsService.rollbackModel(version) });

// --- Health ---
export const useHealth = () =>
  useQuery({ queryKey: ['health'], queryFn: healthService.getHealth, refetchInterval: 30000 });
