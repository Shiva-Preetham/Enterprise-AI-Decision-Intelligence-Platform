"""
Enterprise AI Customer Intelligence Platform — Decision Repository.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decision_engine.models import RecommendationModel, WorkflowModel, ExecutionModel, DecisionHistoryModel

class DecisionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_recommendation(self, recommendation: RecommendationModel) -> RecommendationModel:
        self.session.add(recommendation)
        await self.session.commit()
        await self.session.refresh(recommendation)
        return recommendation

    async def create_workflow(self, workflow: WorkflowModel) -> WorkflowModel:
        self.session.add(workflow)
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def update_workflow_status(self, workflow_id: UUID, status: str) -> Optional[WorkflowModel]:
        stmt = select(WorkflowModel).where(WorkflowModel.workflow_id == workflow_id)
        result = await self.session.execute(stmt)
        workflow = result.scalar_one_or_none()
        if workflow:
            workflow.status = status
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def get_workflow(self, workflow_id: UUID) -> Optional[WorkflowModel]:
        stmt = select(WorkflowModel).where(WorkflowModel.workflow_id == workflow_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recommendation(self, recommendation_id: UUID) -> Optional[RecommendationModel]:
        stmt = select(RecommendationModel).where(RecommendationModel.recommendation_id == recommendation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_execution(self, execution: ExecutionModel) -> ExecutionModel:
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def add_audit_log(self, audit: DecisionHistoryModel) -> DecisionHistoryModel:
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(audit)
        return audit

    async def get_customer_history(self, customer_id: str) -> List[DecisionHistoryModel]:
        stmt = select(DecisionHistoryModel).where(DecisionHistoryModel.customer_unique_id == customer_id).order_by(DecisionHistoryModel.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_workflow_audit(self, workflow_id: UUID) -> List[DecisionHistoryModel]:
        stmt = select(DecisionHistoryModel).where(DecisionHistoryModel.workflow_id == workflow_id).order_by(DecisionHistoryModel.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
