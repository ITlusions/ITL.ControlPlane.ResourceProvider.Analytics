"""
Repository layer for Model Registry resources
"""

from typing import Optional, List
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from itl_analytics_provider.models.orm import Model

logger = logging.getLogger(__name__)


class ModelRepository:
    """Data access layer for model registry"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Model:
        """Create new model record"""
        model = Model(**data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        logger.info(f"Registered model: {model.id}", extra={"model_id": str(model.id)})
        return model

    async def get_by_id(self, model_id: UUID) -> Optional[Model]:
        """Get model by ID"""
        stmt = select(Model).where(Model.id == model_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_subscription(
        self, subscription_id: str, resource_group: str
    ) -> List[Model]:
        """List all models in resource group"""
        stmt = select(Model).where(
            (Model.subscription_id == subscription_id)
            & (Model.resource_group == resource_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, model_id: UUID, data: dict) -> Optional[Model]:
        """Update model metadata"""
        model = await self.get_by_id(model_id)
        if not model:
            return None

        for key, value in data.items():
            setattr(model, key, value)

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete(self, model_id: UUID) -> bool:
        """Delete model record"""
        model = await self.get_by_id(model_id)
        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        logger.info(f"Deleted model: {model_id}")
        return True
