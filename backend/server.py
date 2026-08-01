"""Main gRPC server for Agent Mobile Automation Framework"""

import asyncio
import os
from typing import AsyncGenerator

from backend.device.device_manager import DeviceManager
from backend.ai_agent.agent import AutomationAgent
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class AutomationServer:
    \"\"\"gRPC server for automation service\"\"\"
    
    def __init__(self, port: int = 50051):
        self.port = port
        self.device_manager = DeviceManager(max_concurrent=10)
        self.agent = AutomationAgent(self.device_manager)
    
    async def start(self):
        \"\"\"Start the server\"\"\"
        logger.info(f"Starting Automation Server on port {self.port}")
        
        try:
            # TODO: Implement actual gRPC server
            # For now, just keep the server running
            await self._run_server()
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
    
    async def _run_server(self):
        \"\"\"Run the server loop\"\"\"
        logger.info("Server running. Press Ctrl+C to stop.")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
    
    async def stop(self):
        \"\"\"Stop the server\"\"\"
        logger.info("Stopping server")
        
        # Disconnect all devices
        for device_id in list(self.device_manager.devices.keys()):
            await self.device_manager.unregister_device(device_id)


async def main():
    \"\"\"Main entry point\"\"\"
    port = int(os.environ.get('PORT', 50051))
    
    server = AutomationServer(port)
    
    try:
        await server.start()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        await server.stop()
        raise


if __name__ == '__main__':
    asyncio.run(main())
