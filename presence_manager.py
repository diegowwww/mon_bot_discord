import discord
import random

class PresenceManager:
    def __init__(self, bot):
        self.bot = bot
        self.presences = [
            "En ligne 😎",
            "Avec les commandes !",
            "Bot actif 🔥",
            "Sanchez est là !",
            "Utilise /help pour commencer"
        ]

    async def set_random_presence(self):
        activity = discord.Game(name=random.choice(self.presences))
        await self.bot.change_presence(activity=activity)