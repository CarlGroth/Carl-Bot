import discord
import asyncio
from bot import CarlBot

class commands(CarlBot):
    async def ping(self, message):
        await self.send_message(message.channel, "pong!")