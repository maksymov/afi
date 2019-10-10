# -*- coding: utf-8 -*-

import discord
import urllib.request
import json
import bot_settings

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afi.settings")
import django
django.setup()

from core.views import *
from django.utils.translation import ugettext as _

client = discord.Client()

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

@client.event
async def on_message(message):
    """Отслеживание команд
    Функция запускает бота, следит какие команды отправляются
    боту и возвращает ответ в канал дискорда.

    """
    discord_server_id = message.guild.id
    afi = client.user
    if afi in message.mentions:
        servers = client.guilds
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
        msg = set_lang(message)
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
                await client.change_nickname(u['user'], u['nickname'])
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
                await client.change_nickname(u['user'], u['nickname'])
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
        msg = get_top(message)
        if msg[0] == 'ok':
            colour = 0x2ecc71
        if msg[0] == 'err':
            colour = 0xe74c3c
        embed = discord.Embed(
            description=msg[1],
            colour=colour,
            type='rich',
        )
        await message.channel.send(embed=embed)
client.run(bot_settings.BOT_TOKEN)
