"""
Memory Cell for Dataset resources
"""

from itl_braincell.cells.base import MemoryCell


class DatasetCell(MemoryCell):
    """Dataset management memory cell"""

    def __init__(self):
        super().__init__()
        self.name = "datasets"
        self.prefix = "/api/datasets"

    def get_router(self):
        """Return FastAPI router for this cell"""
        from itl_analytics_provider.routes.datasets import router

        return router

    def get_models(self):
        """Return ORM models for this cell"""
        from itl_analytics_provider.models.orm import Dataset

        return [Dataset]

    def register_mcp_tools(self, mcp):
        """Register MCP tools for this cell

        TODO (Phase 2):
            - @mcp.tool("Register dataset")
            - @mcp.tool("Get dataset schema")
            - @mcp.tool("List datasets")
            - @mcp.tool("Get data lineage")
        """
        pass


cell = DatasetCell()
