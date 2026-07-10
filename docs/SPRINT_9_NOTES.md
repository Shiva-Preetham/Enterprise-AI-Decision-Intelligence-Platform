# Sprint 9 — Enterprise Control Center (Product Experience)

## Overview
Sprint 9 transformed the backend architecture of the Enterprise AI Customer Intelligence Platform into a full-fledged enterprise SaaS product. A production-ready React frontend was built using clean architecture principles.

## Technologies Used
* **React 18**: Component-based UI rendering.
* **TypeScript**: End-to-end type safety matching Pydantic schemas.
* **Vite**: Ultra-fast build tool and development server.
* **TailwindCSS**: Utility-first CSS framework for a responsive, dark-mode-first design system.
* **Radix UI + Lucide**: Accessible primitives and standard enterprise iconography.
* **TanStack Query**: Data fetching, caching, and state management.
* **Axios**: HTTP client equipped with JWT interceptors.
* **Recharts**: Responsive charting for analytics and MLOps visualizations.

## Key Modules Implemented (15 Pages)
1. **Executive Dashboard**: High-level KPIs, Churn Trends, Revenue at Risk.
2. **Customer List**: Searchable, paginated table of customers with risk badges.
3. **Customer 360**: Individual profile, feature store data, SHAP waterfall explanation, and event timeline.
4. **AI Copilot**: LangGraph-powered conversational interface simulating an enterprise business analyst.
5. **Workflow Center**: Visual tracking of recommendation workflows through execution states.
6. **Approval Center**: Human-in-the-loop (HITL) interface for reviewing and approving actions.
7. **Recommendation Center**: Filterable table of all generated business recommendations.
8. **Audit Explorer**: Chronological audit trail linking policy evaluation to execution.
9. **Model Registry**: Version control view for ML models with comparison charts and rollback capabilities.
10. **Drift Dashboard**: Population Stability Index (PSI) visualization for monitoring feature drift.
11. **Feature Store Explorer**: Data quality and distribution metrics for engineered features.
12. **MLOps Dashboard**: System observability showing API latency, subsystem health, and active inferences.
13. **Alerts Center**: Aggregation of drift, cache, and system health alerts.
14. **Admin Panel**: User role management and global platform feature flags.
15. **Architecture Explorer**: Interactive map of the end-to-end data pipeline and platform architecture.
16. **Demo Mode**: Guided, auto-playing walk-through simulating a customer's churn journey through prediction, approval, and execution.

## Architectural Notes
The UI relies heavily on a custom Design System specified in `globals.css` using modern CSS variables. Reusable atomic components (`Card`, `Badge`, `Button`, `StatusBadge`, `KPICard`) were built from scratch to guarantee visual consistency. 

A mock Authentication flow with JWT capabilities ensures the application correctly handles Role-Based Access Control (RBAC).

## Status
**Completed.** The Enterprise AI Customer Intelligence Platform is now fully visualized, observable, and usable by end-users (Admins, Managers, Analysts). The frontend correctly proxies to the existing FastAPI backend.
