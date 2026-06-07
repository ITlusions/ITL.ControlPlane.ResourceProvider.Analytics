"""
Main entry point for Analytics Provider
"""

import os
import logging
import sys
from .initialization import AnalyticsProviderServer
from .config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point

    Runs Analytics Provider Server
    """
    settings = get_settings()

    try:
        host = os.getenv("PROVIDER_HOST", "0.0.0.0")
        port = int(os.getenv("PROVIDER_PORT", settings.service_port))

        server = AnalyticsProviderServer()
        server.run(host=host, port=port, log_level="info")

    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
