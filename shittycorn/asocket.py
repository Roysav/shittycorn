import socket
import asyncio


class Socket(socket.socket):
    async def aaccept(self):
        return await asyncio.to_thread(self.accept)

