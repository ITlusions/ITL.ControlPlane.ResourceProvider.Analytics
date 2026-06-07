"""
Memory Cell for Analytics Job resources
"""

from itl_braincell.cells.base import MemoryCell


class AnalyticsJobCell(MemoryCell):
    """Analytics Job memory cell"""

    def __init__(self):
        super().__init__()
        self.name = "analytics_jobs"
        self.prefix = "/api/analytics-jobs"

    def get_router(self):
        """Return FastAPI router for this cell"""
        from itl_analytics_provider.routes.jobs import router

        return router

    def get_models(self):
        """Return ORM models for this cell"""
        from itl_analytics_provider.models.orm import AnalyticsJob

        return [AnalyticsJob]

    def register_mcp_tools(self, mcp):
        """Register MCP tools for this cell

        TODO (Phase 2):
            - @mcp.tool("Submit analytics job")
            - @mcp.tool("Get job status")
            - @mcp.tool("List jobs")
            - @mcp.tool("Cancel job")
        """
        pass


cell = AnalyticsJobCell()
