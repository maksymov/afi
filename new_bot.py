# -*- coding: utf-8 -*-

import bot_settings
import discord
import os
import django
from discord import app_commands
from typing import Optional, List
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afi.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from core.views import *

MY_GUILD = discord.Object(id=305986295375724555)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command(name='статка')
@app_commands.rename(player='игрок')
@app_commands.describe(player='Выбери игрока для просмотра статки')
async def stat(interaction: discord.Interaction, player: Optional[discord.Member] = None):
    """Статистика игрока"""
    user = interaction.user
    if player:
        user = player
    msg = player_stat(interaction.guild_id, user)
    embed = discord.Embed(
        description=msg,
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


async def award_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    awards = get_award_choices(interaction.guild_id)
    return [
        app_commands.Choice(name=award, value=award)
        for award in awards if current.lower() in award.lower()
    ]


@client.tree.command(name='награда')
@app_commands.rename(
    action='действие',
    award_title='награда',
    player='игрок'
)
@app_commands.describe(
    action='Выбери действие',
    award_title='Выбери награду',
    player='Выбери игрока'
)
@app_commands.choices(action=[
    app_commands.Choice(name="Вручить", value="+"),
    app_commands.Choice(name="Снять", value="-"),
])
@app_commands.autocomplete(award_title=award_autocomplete)
#@app_commands.choices(award_title=award_choices(discord.Interaction.guild_id))
async def award(interaction: discord.Interaction,
                action: app_commands.Choice[str],
                player: discord.Member,
                award_title: str):
    """Вручение и снятие наград"""
    if action.value == '+':
        msg = player_award_add(
            discord_server_id=interaction.guild_id,
            user=player,
            author=interaction.user,
            award_title=award_title
        )
    embed = discord.Embed(
        description=msg[1],
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)
    if msg[0] == 'ok' and msg[2]:
        try:
            await player.edit(nick=msg[2])
        except:
            pass


client.run(bot_settings.BOT_TOKEN)
