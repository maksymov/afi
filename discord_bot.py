# -*- coding: utf-8 -*-

import discord
import urllib.request
import json
import bot_settings
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash import SlashCommandOptionType
from discord_slash.utils import manage_commands
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afi.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
import django
django.setup()
from core.views import *
from django.utils.translation import ugettext as _


description = "Бот AFI"
bot = commands.Bot(command_prefix='!', description=description, intents=discord.Intents.all())
slash = SlashCommand(bot, auto_register=True, auto_delete=True)

guild_ids = [305986295375724555]

nick = [u"!ник", u"!nick"]
stat = [u"!статка", u"!stat"]
ranks = [u"!звания", u"!ranks"]
awards = [u"!награды", u"!awards"]
rank_add = [u"!звание+", u"!rank+"]
rank_remove = [u"!звание-", u"!rank-"]
award_add = [u"!награда+", u"!award+"]
award_remove = [u"!награда-", u"!award-"]
create_award_in_database = [u"!добавить-награду-в-базу-данных", u"!create-award-in-database"]
delete_award_from_database = [u"!удалить-награду-из-базы-данных", u"!delete-award-from-database"]
edit_award_in_database = [u"!изменить-награду", u"!edit-award"]
create_rank_in_database = [u"!добавить-звание-в-базу-данных", u"!create-rank-in-database"]
delete_rank_from_database = [u"!удалить-звание-из-базы-данных", u"!delete-rank-from-database"]
edit_rank_in_database  = [u"!изменить-звание", u"!edit-rank"]
top = [u"!топ", u"!top"]


test_guild_ids = [305986295375724555]


# ------------
# СЛЭШ-КОМАНДЫ
# ------------


@slash.slash(name="топ",
    description="Топ 10 игроков за указанный период",
    options=[
        manage_commands.create_option("начальная_дата", "Дата в фрмате ГГГГ-ММ-ДД", SlashCommandOptionType.STRING, True),
        manage_commands.create_option("конечная_дата", "Дата в фрмате ГГГГ-ММ-ДД", SlashCommandOptionType.STRING, True)
    ])
async def _top(ctx, start, end):
    msg = get_top(ctx.author.id, ctx.guild.id, start, end)
    embed = discord.Embed(
            description=msg[1],
            colour=0x2ecc71,
            type='rich')
    await ctx.channel.send(embed=embed)


@slash.slash(name="язык",
    description="Выбор языка пользователя",
    options=[{
        "name": "выбрать",
        "description": "Выбор языка пользователя",
        "type": 3,
        "required": True,
        "choices": [{
            "name": "Русский",
            "value": "ru"
        },{
            "name": "English",
            "value": "en"
        }]
    }])
async def _lang(ctx, lang):
    msg = set_lang(ctx.author.id, ctx.guild.id, lang)
    embed = discord.Embed(
            description=msg,
            colour=0x2ecc71,
            type='rich')
    await ctx.channel.send(embed=embed)


@slash.slash(name="награда",
    description="Вручение и отбор наград",
    options=[{
        "name": "действие",
        "description": "Вручить или отнять",
        "type": 3,
        "required": True,
        "choices": [{
                "name": "Вручить",
                "value": "+"
            },{
                "name": "Отнять (пока не работает)",
                "value": "-"
        }]
    },{
        "name": "игрок",
        "description": "Укажите, кму вручается награда",
        "type": 6,
        "required": True,
    },{
        "name": "награда",
        "description": "Укажите награду",
        "type": 3,
        "required": True,
    }])
async def _award(ctx, action, user, award_title):
    if action == '+':
        msg = player_award_add(discord_server_id=ctx.guild.id,
                user=user,
                author=ctx.author,
                award_title=award_title)
    #if action == '-':
    #    msg = player_award_delete(ctx.guild.id, start, end)
        embed = discord.Embed(
                description=msg[1],
                colour=0x2ecc71,
                type='rich')
        if ctx.author.nick:
            footer = "Награду вручил %s" % (ctx.author.nick)
        else:
            footer = "Награду вручил %s" % (ctx.author.name)
        embed.set_footer(text=footer)
        await ctx.channel.send(embed=embed)
        if msg[0] == 'ok':
            try:
                await user.edit(nick=msg[2])
            except:
                pass

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# ----------------
# КОМАНДЫ ОТДЕЛЬНО
# ----------------


@bot.command()
async def ping(ctx):
    print('test')
    await ctx.send('pong')


# ----------
# СТАРЫЙ КОД
# ----------


@bot.event
async def on_message(message):
    """Отслеживание команд
    Функция запускает бота, следит какие команды отправляются
    боту и возвращает ответ в канал дискорда.

    """
    discord_server_id = message.guild.id
    afi = bot.user
    if afi in message.mentions:
        servers = bot.guilds
        num = len(servers)
        text = u'{0.author.mention}, ' + _(u'вся инфа про меня здесь: ')\
               + u'<https://github.com/maksymov/afi/blob/master/README.md> \n' \
               + _(u'Discord-сервер тех. поддержки:') + ' <https://discord.gg/Gqza8FD> \n' \
               + _(u'Работаю на ') + str(num) + _(u' серверах!')
        msg = text.format(message)
        embed = discord.Embed(
            description=msg,
            colour=0x2ecc71,
            type='rich',
        )
        await message.channel.send(embed=embed)
    # =======================
    # Выбор языка для сервера
    elif message.content.startswith(u'!lang'):
        discord_server_id = message.guild.id
        discord_id = message.author.id
        message_text = message.clean_content
        lang = message_text[message_text.find("(") + 1:message_text.find(")")]
        msg = set_lang(discord_id, discord_server_id, lang)
        embed = discord.Embed(
            description=msg,
            colour=0x2ecc71,
            type='rich',
        )
        await message.channel.send(embed=embed)
    # ======================
    # ПРИВЯЗКА ИГРОВОГО НИКА
    elif message.content.startswith(tuple(nick)):
        msg = player_nick(message)
        embed = discord.Embed(
            description=msg,
            colour=0x2ecc71,
            type='rich',
        )
        await message.channel.send(embed=embed)
    # ===========================
    # ПОЛУЧЕНИЕ СТАТИСТИКИ ИГРОКА
    elif message.content.startswith(tuple(stat)):
        if not message.mentions:
            message.mentions.append(message.author)
        msg = player_stat(message)
        embed = discord.Embed(
            description=msg,
            colour=0x2ecc71,
            type='rich',
        )
        await message.channel.send(embed=embed)
    # ======================
    # СПИСОК ПОЛКОВЫХ ЗВАНИЙ
    elif message.content.startswith(tuple(ranks)):
        msg = squad_ranks(message)
        embed = discord.Embed(
            description=msg,
            colour=0x2ecc71,
            type='rich',
        )
        await message.channel.send(embed=embed)
    # ======================
    # СПИСОК ПОЛКОВЫХ НАГРАД
    elif message.content.startswith(tuple(awards)):
        msg = squad_awards(message)
        embed = discord.Embed(
            description=msg,
            colour=0x2ecc71,
            type='rich',
        )
        await message.channel.send(embed=embed)
    # ========================
    # ПРИСВОЕНИЕ ЗВАНИЯ ИГРОКУ
    elif message.content.startswith(tuple(rank_add)):
        msg = player_rank_add(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # ============================
    # РАЗЖАЛОВАНИЕ В ЗВАНИИ ИГРОКА
    elif message.content.startswith(tuple(rank_remove)):
        msg = player_rank_remove(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # =======================
    # ВРУЧЕНИЕ НАГРАДЫ ИГРОКУ
    elif message.content.startswith(tuple(award_add)):
        msg, users = player_award_add(message)
        for u in users:
            try:
                await u['user'].edit(nick=u['nickname'])
            except:
                pass
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # =======================
    # ОТБОР НАГРАДЫ ИГРОКА
    elif message.content.startswith(tuple(award_remove)):
        msg, users = player_award_delete(message)
        for u in users:
            try:
                await u['user'].edit(nick=u['nickname'])
            except:
                pass
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # =========================
    # СОЗДАНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(tuple(create_award_in_database)):
        msg = award_create(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # =========================
    # УДАЛЕНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(tuple(delete_award_from_database)):
        msg = award_delete(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # ===============================
    # РЕДАКТИРОВАНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(tuple(edit_award_in_database)):
        msg = award_edit(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # =========================
    # СОЗДАНИЕ ПОЛКОВОГО ЗВАНИЯ
    elif message.content.startswith(tuple(create_rank_in_database)):
        msg = rank_create(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # =========================
    # УДАЛЕНИЕ ПОЛКОВОГО ЗВАНИЯ
    elif message.content.startswith(tuple(delete_rank_from_database)):
        msg = rank_delete(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # ===============================
    # РЕДАКТИРОВАНИЕ ПОЛКОВОГО ЗВАНИЯ
    elif message.content.startswith(tuple(edit_rank_in_database)):
        msg = rank_edit(message)
        if msg[0] == 'ok':
            await message.add_reaction("👌")
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    # =====================
    # ТОП ИГРОКОВ ЗА ПЕРИОД
    elif message.content.startswith(tuple(top)):
        message_text = message.clean_content
        start = message_text[message_text.find("(") + 1:message_text.find(")")]
        end = message_text[message_text.find("[") + 1:message_text.find("]")]
        msg = get_top(message.author.id, message.guild.id, start, end)
        if msg[0] == 'ok':
            await message.channel.send(msg[1])
        if msg[0] == 'err':
            embed = discord.Embed(
                description=msg[1],
                colour=0xe74c3c,
                type='rich',
            )
            await message.channel.send(embed=embed)
    await bot.process_commands(message)
bot.run(bot_settings.BOT_TOKEN)
