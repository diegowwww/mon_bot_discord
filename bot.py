import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from presence_manager import PresenceManager

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

TOKEN = os.getenv("MTM1Njc1MDc4NjQzNjI3MjI3MQ.G8PGgH.6dB2OEDB99377MvCba7R04Fgqc6wCKH9XfeCic")

bot = commands.Bot(command_prefix="!", intents=intents)     
presence_manager = PresenceManager()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Connecté en tant que {bot.user}.")

# /ping
@bot.tree.command(name="ping", description="Test de latence du bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong 🏓 ! Latence : {round(bot.latency * 1000)}ms")

# /commandes
@bot.tree.command(name="commandes", description="Liste des commandes disponibles")
async def commandes(interaction: discord.Interaction):
    cmds = [
        "`/ping` → Vérifie si le bot est réactif",
        "`/commandes` → Liste des commandes",
        "`/presence config` → Configure les rôles liés aux réactions",
        "`/presence create` → Crée un message de présence"
    ]
    await interaction.response.send_message("📋 Commandes disponibles :\n" + "\n".join(cmds))

# /presence config
@bot.tree.command(name="presence_config", description="Configurer un emoji et un rôle pour la présence")
@app_commands.describe(emoji="Emoji utilisé", role="Rôle attribué")
async def presence_config(interaction: discord.Interaction, emoji: str, role: discord.Role):
    presence_manager.set_config(interaction.guild.id, emoji, role.id)
    await interaction.response.send_message(f"Configuration ajoutée : {emoji} → {role.name}")

# /presence create
@bot.tree.command(name="presence_create", description="Créer un message de présence avec réactions")
@app_commands.describe(message="Message à afficher")
async def presence_create(interaction: discord.Interaction, message: str):
    config = presence_manager.get_config(interaction.guild.id)

    if not config:
        await interaction.response.send_message("Aucune configuration trouvée. Utilise `/presence config` d'abord.")
        return

    msg = await interaction.channel.send(message)

    for emoji in config.keys():
        await msg.add_reaction(emoji)

    presence_manager.set_message(interaction.guild.id, msg.id)
    await interaction.response.send_message("Message de présence envoyé ✅")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    guild_id = payload.guild_id
    emoji = str(payload.emoji)
    config = presence_manager.get_config(guild_id)
    message_id = presence_manager.get_message(guild_id)

    if str(payload.message_id) != str(message_id):
        return

    if emoji in config:
        guild = bot.get_guild(guild_id)
        role = guild.get_role(config[emoji])
        if role:
            member = guild.get_member(payload.user_id)
            await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    guild_id = payload.guild_id
    emoji = str(payload.emoji)
    config = presence_manager.get_config(guild_id)
    message_id = presence_manager.get_message(guild_id)

    if str(payload.message_id) != str(message_id):
        return

    if emoji in config:
        guild = bot.get_guild(guild_id)
        role = guild.get_role(config[emoji])
        if role:
            member = guild.get_member(payload.user_id)
            await member.remove_roles(role)

bot.run(TOKEN)