import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import DashboardLayout from '../layouts/DashboardLayout';

// Lazy-loaded pages for code splitting
const Dashboard = lazy(() => import('../pages/Dashboard'));
const CustomerList = lazy(() => import('../pages/CustomerList'));
const Customer360 = lazy(() => import('../pages/Customer360'));
const AICopilot = lazy(() => import('../pages/AICopilot'));
const WorkflowCenter = lazy(() => import('../pages/WorkflowCenter'));
const ApprovalCenter = lazy(() => import('../pages/ApprovalCenter'));
const RecommendationCenter = lazy(() => import('../pages/RecommendationCenter'));
const AuditExplorer = lazy(() => import('../pages/AuditExplorer'));
const ModelRegistry = lazy(() => import('../pages/ModelRegistry'));
const DriftDashboard = lazy(() => import('../pages/DriftDashboard'));
const FeatureStoreExplorer = lazy(() => import('../pages/FeatureStoreExplorer'));
const MLOpsDashboard = lazy(() => import('../pages/MLOpsDashboard'));
const AlertsCenter = lazy(() => import('../pages/AlertsCenter'));
const AdminPanel = lazy(() => import('../pages/AdminPanel'));
const ArchitectureExplorer = lazy(() => import('../pages/ArchitectureExplorer'));
const DemoMode = lazy(() => import('../pages/DemoMode'));
const Login = lazy(() => import('../pages/Login'));

function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <SuspenseWrapper><Login /></SuspenseWrapper>,
  },
  {
    path: '/',
    element: <DashboardLayout />,
    children: [
      { index: true, element: <SuspenseWrapper><Dashboard /></SuspenseWrapper> },
      { path: 'customers', element: <SuspenseWrapper><CustomerList /></SuspenseWrapper> },
      { path: 'customers/:id', element: <SuspenseWrapper><Customer360 /></SuspenseWrapper> },
      { path: 'copilot', element: <SuspenseWrapper><AICopilot /></SuspenseWrapper> },
      { path: 'workflows', element: <SuspenseWrapper><WorkflowCenter /></SuspenseWrapper> },
      { path: 'approvals', element: <SuspenseWrapper><ApprovalCenter /></SuspenseWrapper> },
      { path: 'recommendations', element: <SuspenseWrapper><RecommendationCenter /></SuspenseWrapper> },
      { path: 'audit', element: <SuspenseWrapper><AuditExplorer /></SuspenseWrapper> },
      { path: 'models', element: <SuspenseWrapper><ModelRegistry /></SuspenseWrapper> },
      { path: 'drift', element: <SuspenseWrapper><DriftDashboard /></SuspenseWrapper> },
      { path: 'features', element: <SuspenseWrapper><FeatureStoreExplorer /></SuspenseWrapper> },
      { path: 'mlops', element: <SuspenseWrapper><MLOpsDashboard /></SuspenseWrapper> },
      { path: 'alerts', element: <SuspenseWrapper><AlertsCenter /></SuspenseWrapper> },
      { path: 'admin', element: <SuspenseWrapper><AdminPanel /></SuspenseWrapper> },
      { path: 'architecture', element: <SuspenseWrapper><ArchitectureExplorer /></SuspenseWrapper> },
      { path: 'demo', element: <SuspenseWrapper><DemoMode /></SuspenseWrapper> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);
