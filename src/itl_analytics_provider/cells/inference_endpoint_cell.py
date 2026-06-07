"""
Memory Cell for Inference Endpoint resources
"""

from itl_braincell.cells.base import MemoryCell


class InferenceEndpointCell(MemoryCell):
    """Model serving memory cell"""

    def __init__(self):
        super().__init__()
        self.name = "inference_endpoints"
        self.prefix = "/api/inference-endpoints"

    def get_router(self):
        """Return FastAPI router for this cell"""
        from itl_analytics_provider.routes.inference import router

        return router

    def get_models(self):
        """Return ORM models for this cell"""
        from itl_analytics_provider.models.orm import InferenceEndpoint

        return [InferenceEndpoint]

    def register_mcp_tools(self, mcp):
        """Register MCP tools for this cell

        TODO (Phase 3):
            - @mcp.tool("Deploy inference endpoint")
            - @mcp.tool("Get endpoint status")
            - @mcp.tool("List endpoints")
            - @mcp.tool("Get predictions")
        """
        pass


cell = InferenceEndpointCell()
