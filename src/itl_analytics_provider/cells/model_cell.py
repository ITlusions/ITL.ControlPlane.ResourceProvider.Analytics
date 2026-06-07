"""
Memory Cell for Model Registry resources
"""

from itl_braincell.cells.base import MemoryCell


class ModelCell(MemoryCell):
    """Model Registry memory cell"""

    def __init__(self):
        super().__init__()
        self.name = "models"
        self.prefix = "/api/models"

    def get_router(self):
        """Return FastAPI router for this cell"""
        from itl_analytics_provider.routes.models import router

        return router

    def get_models(self):
        """Return ORM models for this cell"""
        from itl_analytics_provider.models.orm import Model

        return [Model]

    def register_mcp_tools(self, mcp):
        """Register MCP tools for this cell

        TODO (Phase 3):
            - @mcp.tool("Register model")
            - @mcp.tool("Get model details")
            - @mcp.tool("List models")
            - @mcp.tool("Get model versions")
        """
        pass


cell = ModelCell()
