"""
Notebook handler mixin — business logic for notebook resources

Follows Core provider pattern:
- Handler methods: _create_notebook, _get_notebook, _list_notebooks, _delete_notebook
- Uses self.engine.session() for database access
- Returns domain objects; let routes handle response mapping
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from itl_controlplane_sdk.analytics import Notebook, NotebookStatus

logger = logging.getLogger(__name__)


class NotebookHandlerMixin:
    """Handler for notebook operations"""

    async def _create_notebook(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: Dict[str, Any],
        owner_id: str,
    ) -> Notebook:
        """Create notebook session
        
        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            name: Notebook name
            location: Azure region
            properties: Notebook properties
            owner_id: User ID

        Returns:
            Created Notebook ORM instance
        """
        logger.info(
            f"Creating notebook {name}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        # Get repository from engine session
        async with self.engine.session() as session:
            from ..repositories.notebook_repo import NotebookRepository

            repo = NotebookRepository(session)

            # Create initial record (status: Creating)
            notebook = await repo.create(
                {
                    "subscription_id": subscription_id,
                    "resource_group": resource_group,
                    "name": name,
                    "location": location,
                    "status": NotebookStatus.CREATING.value,
                    "owner_id": owner_id,
                    "kernel": properties.get("kernel", "python3"),
                    "compute_sku": properties.get("computeSku", "standard"),
                }
            )

            logger.info(f"Notebook created: {notebook.id}")
            return notebook

    async def _get_notebook(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[Notebook]:
        """Get notebook by ARM path
        
        Args:
            subscription_id: Subscription ID
            resource_group: Resource group name
            name: Notebook name

        Returns:
            Notebook ORM instance or None
        """
        async with self.engine.session() as session:
            from ..repositories.notebook_repo import NotebookRepository

            repo = NotebookRepository(session)
            return await repo.get_by_name(subscription_id, resource_group, name)

    async def _list_notebooks(
        self, subscription_id: str, resource_group: str
    ) -> List[Notebook]:
        """List notebooks in resource group
        
        Args:
            subscription_id: Subscription ID
            resource_group: Resource group name

        Returns:
            List of Notebook ORM instances
        """
        async with self.engine.session() as session:
            from ..repositories.notebook_repo import NotebookRepository

            repo = NotebookRepository(session)
            return await repo.list_by_subscription(subscription_id, resource_group)

    async def _delete_notebook(
        self, subscription_id: str, resource_group: str, name: str
    ) -> bool:
        """Delete notebook
        
        Args:
            subscription_id: Subscription ID
            resource_group: Resource group name
            name: Notebook name

        Returns:
            True if deleted, False if not found
        """
        async with self.engine.session() as session:
            from ..repositories.notebook_repo import NotebookRepository

            repo = NotebookRepository(session)
            notebook = await repo.get_by_name(subscription_id, resource_group, name)
            if not notebook:
                return False

            return await repo.delete(notebook.id)

    async def _update_notebook_status(
        self, notebook_id: UUID, status: NotebookStatus
    ) -> Optional[Notebook]:
        """Update notebook status
        
        Args:
            notebook_id: Notebook ID
            status: New status

        Returns:
            Updated Notebook or None if not found
        """
        async with self.engine.session() as session:
            from ..repositories.notebook_repo import NotebookRepository

            repo = NotebookRepository(session)
            return await repo.update(notebook_id, {"status": status.value})
