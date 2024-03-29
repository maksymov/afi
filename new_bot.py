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
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        if bot_settings.TEST_GUILD:
            TEST_GUILD = discord.Object(id=305986295375724555)
            self.tree.copy_global_to(guild=TEST_GUILD)
            await self.tree.sync(guild=TEST_GUILD)
        else:
            await self.tree.sync()


intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


# ===============================
# Автодополнение названия награды
# ===============================
async def award_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    awards = get_award_choices(interaction.guild_id)
    return [
        app_commands.Choice(name=award, value=award)
        for award in awards if current.lower() in award.lower()
    ]


# =============
# Описание бота
# =============

@client.tree.command(name='абамне')
async def awards(interaction: discord.Interaction):
    """Описание бота и ссылки"""
    servers = client.guilds
    num = len(servers)
    msg = "[GitHub](https://github.com/maksymov/afi/blob/master/README.md) | " \
           + "[Discord-сервер тех. поддержки](https://discord.gg/Gqza8FD) \n" \
           + '[Пригласить бот на свой сервер](https://discord.com/api/oauth2/authorize?client_id=304296578989162496&permissions=134597696&scope=bot%20applications.commands) \n' \
           + 'Работаю на ' + str(num) + ' серверах!'
    if interaction.user.id == 201722649708199936:
        for s in servers:
            msg += '\n **%s** - %s' % (s.member_count, s.name)
    embed = discord.Embed(
        description=msg,
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


# ======================
# Привязка игрового ника
# ======================

@client.tree.command(name='ник')
@app_commands.rename(nick='ник')
@app_commands.describe(nick='Укажи свой ник в WarThunder')
async def nick(
        interaction: discord.Interaction,
        nick: str):
    """Привязка игрового ника"""
    locale = interaction.locale.value[:2]
    msg = set_player_nick(locale, interaction.guild_id, interaction.user.id, nick)
    embed = discord.Embed(
        description=msg,
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================
# Просмотр статистики игрока
# ==========================

@client.tree.command(name='статка')
@app_commands.rename(player='игрок', nick='ник')
@app_commands.describe(
        player='Выбери игрока для просмотра статки',
        nick='Напиши ник в тундре')
async def stat(interaction: discord.Interaction,
        player: Optional[discord.Member] = None,
        nick: str = None):
    """Статистика игрока"""
    locale = interaction.locale.value[:2]
    user = interaction.user
    if player:
        user = player
    msg = player_stat(locale, interaction.guild_id, user, nick)
    embed = discord.Embed(
        description=msg,
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


# ========================
# Вручение и снятие наград
# ========================

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
async def award(interaction: discord.Interaction,
                action: app_commands.Choice[str],
                player: discord.Member,
                award_title: str):
    """Вручение и снятие наград"""
    locale = interaction.locale.value[:2]
    # ----------------
    # Вручение награды
    if action.value == '+':
        msg = player_award_add(locale,
            guild_id=interaction.guild_id,
            user=player,
            author=interaction.user,
            award_title=award_title
        )
    # --------------
    # Снятие награды
    if action.value == '-':
        msg = player_award_delete(locale,
            guild_id=interaction.guild_id,
            user=player,
            author=interaction.user,
            award_title=award_title
        )
    # -------------------
    # Формирование ответа
    if msg[0] == 'ok':
        colour = 0x2ecc71
    if msg[0] == 'err':
        colour = 0xdd2727
    embed = discord.Embed(
        description=msg[1],
        colour=colour,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)
    if msg[0] == 'ok' and msg[2]:
        try:
            await player.edit(nick=msg[2])
        except:
            pass


# ======================
# Список полковых наград
# ======================

@client.tree.command(name='полковые_награды_список')
async def awards(interaction: discord.Interaction):
    """Список полковых наград"""
    locale = interaction.locale.value[:2]
    msg = squad_awards(locale, interaction.guild_id)
    embed = discord.Embed(
        description=msg,
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


# ======================
# Настройка наград
# ======================

@client.tree.command(name='полковые_награды_настройка')
@app_commands.rename(
    action='действие',
    award_title='назвние',
    award_desc='описание',
    award_icon='иконка',
    award_order='номер',
    award_cost='голды',)
@app_commands.choices(action=[
    app_commands.Choice(name="Создать", value="add"),
    app_commands.Choice(name="Изменить", value="edit"),
])
@app_commands.autocomplete(award_title=award_autocomplete)
async def award_admin(interaction: discord.Interaction,
        action: str,
        award_title: str,
        award_desc: str,
        award_icon: str,
        award_order: str,
        award_cost: str,
        ):
    """Настройка наград полка. Создание и изменение"""
    locale = interaction.locale.value[:2]
    # ----------------
    # Создание награды
    if action == 'add':
        msg = award_create(
            locale,
            interaction.guild_id,
            interaction.user,
            award_title,
            award_desc,
            award_icon,
            award_order,
            award_cost)
    # ----------------
    # Удаление награды
    if action == 'edit':
        msg = award_edit(
            locale,
            interaction.guild_id,
            interaction.user,
            award_title,
            award_desc,
            award_icon,
            award_order,
            award_cost)
    # -------------------
    # Формирование ответа
    if msg[0] == 'ok':
        colour = 0x2ecc71
    if msg[0] == 'err':
        colour = 0xdd2727
    embed = discord.Embed(
        description=msg[1],
        colour=colour,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


# ========================
# Удаление подковых наград
# ========================

@client.tree.command(name='полковые_награды_удаление')
@app_commands.rename(award_title='назвние',)
@app_commands.describe(award_title='Напиши название награды для удаления')
@app_commands.autocomplete(award_title=award_autocomplete)
async def award_admin_delete(interaction: discord.Interaction, award_title: str):
    """Удаление полковых наград из базы данных"""
    locale = interaction.locale.value[:2]
    msg = award_delete(
            locale,
            interaction.guild_id,
            interaction.user,
            award_title)
    if msg[0] == 'ok':
        colour = 0x2ecc71
    if msg[0] == 'err':
        colour = 0xdd2727
    embed = discord.Embed(
        description=msg[1],
        colour=colour,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


# =====================
# ТОП игроков за период
# =====================

@client.tree.command(name='топ')
@app_commands.rename(start='начало', end='конец')
@app_commands.describe(start='Начальная дата', end='Конечная дата')
async def top(interaction: discord.Interaction, start: str = None, end: str = None):
    """Список полковых наград"""
    locale = interaction.locale.value[:2]
    msg = get_top(locale, interaction.guild_id, start, end)
    embed = discord.Embed(
        description=msg[1],
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


# =====================
# Подсчёт кол-ва голды
# =====================

@client.tree.command(name='голда')
@app_commands.rename(start='начало', end='конец')
@app_commands.describe(start='Начальная дата', end='Конечная дата')
async def top(interaction: discord.Interaction, start: str = None, end: str = None):
    """Рассчёт голды для каждого игрока за период"""
    locale = interaction.locale.value[:2]
    msg = get_money(locale, interaction.guild_id, start, end)
    embed = discord.Embed(
        description=msg[1],
        colour=0x2ecc71,
        type='rich',
    )
    await interaction.response.send_message(embed=embed)


# ===========
# Запуск бота
# ===========

client.run(bot_settings.BOT_TOKEN)
